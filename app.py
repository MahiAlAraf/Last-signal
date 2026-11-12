import os
import random
from datetime import timedelta

from flask import (Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for)

import chatbot
import Content_data
import Data
import tools
from get_story import add_points, top_genre
from icons import icon
from search_spacecraft import fetch_details

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
app.permanent_session_lifetime = timedelta(days=365)

app.add_template_global(icon)
SLIDES = [
    ("bg1.jpg", "object1.webp"),
    ("bg2.jpg", "object2.webp"),
    ("bg3.jpg", "object3.webp"),
    ("bg4.jpg", "object4.webp"),
]
STORY_TITLES = ["LAUNCH", "THE MISSION", "THE END", "WHERE I AM NOW", "THE SCIENCE I LEFT BEHIND"]

details_cache = {}   # spacecraft id          -> Wikipedia text + NASA pictures
story_cache = {}     # (spacecraft id, level) -> the story Gemini wrote

#___________________________get profile form session________________________________________
def get_profile():
    
    name = session.get("name")
    if not name:
        return None
    return {
        "name": name,
        "points": session.get("points", 0),
        "stories": session.get("stories", []),
    }


def add_progress(story_id, points_gained):

    stories = session.get("stories", [])
    if story_id not in stories:
        stories.append(story_id)
    session["stories"] = stories                      # put it back so Flask saves it
    session["points"] = session.get("points", 0) + points_gained


def check_name(name):
    """Return an error message if the name is not allowed, or None if it is fine."""
    if name == "":
        return "Name cannot be empty. Please try again."
    if len(name) > tools.MAX_NAME_LENGTH:
        return f"Name is too long (max {tools.MAX_NAME_LENGTH} characters). Please try again."
    return None



# 3. ____________________________________BEFORE EVERY PAGE________________________________
@app.before_request
def ask_new_visitors_for_their_name():
    if request.endpoint in ("welcome", "static"):
        return None                                   
    if request.endpoint is not None and get_profile() is None:
        return redirect(url_for("welcome"))
    return None


@app.context_processor
def add_shared_values():
    values = {"slides": SLIDES, "player": None}

    profile = get_profile()
    if profile is not None:
        values["player"] = {
            "name": profile["name"],
            "level": tools.get_level(profile["points"]),
            "points": profile["points"],
            "stories_read": len(profile["stories"]),
            "stories_total": len(Data.Spacecraft),
            "next_level": tools.points_to_next_level(profile["points"]),  # (name, points) or None
        }
    return values

#_____________________________________________________existence checking____________________________________________
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    if get_profile() is not None:
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        error = check_name(name)
        if error is None:
            session.permanent = True
            session["name"] = name
            session["points"] = 0             
            session["stories"] = []
            return redirect(url_for("home"))

    return render_template("welcome.html", error=error, max_name=tools.MAX_NAME_LENGTH)


@app.route("/")
def home():
    return render_template("home.html")


# ---------------------------------------------------- Find your signal (story picker)
@app.route("/find")
def find_start():
    session["quiz"] = {}                                  # forget old answers
    return redirect(url_for("find_question", step=1))


@app.route("/find/<int:step>", methods=["GET", "POST"])
def find_question(step):
    total = len(Data.Questions)
    if step < 1 or step > total:
        abort(404)
    question = Data.Questions[step - 1]                   # steps start at 1, lists at 0

    if request.method == "POST":
        answer = request.form.get("answer")               # "yes" or "no" (the button clicked)
        if answer not in ("yes", "no"):
            return redirect(url_for("find_question", step=step))

        quiz = session.get("quiz", {})
        quiz[str(step)] = answer
        session["quiz"] = quiz

        if step == total:
            return redirect(url_for("find_results"))
        return redirect(url_for("find_question", step=step + 1))

    return render_template("question.html", question=question, step=step, total=total)


@app.route("/find/results")
def find_results():
    quiz = session.get("quiz", {})
    if len(quiz) < len(Data.Questions):                   # quiz not finished: start again
        return redirect(url_for("find_start"))

    # Same logic as the terminal get_story(): every answer adds points to some tags.
    scoreboard = Data.scoreboard()
    for number, question in enumerate(Data.Questions, start=1):
        answer = quiz[str(number)]                        # "yes" or "no"
        add_points(scoreboard, question[answer])          # question["yes"] or question["no"]

    content_list = Content_data.get_content_List(top_genre(scoreboard))
    return render_template("results.html", content_list=content_list,
                           read=get_profile()["stories"])


# ---------------------------------------------------- Stories (the whole archive)
@app.route("/stories")
def stories():
    return render_template("stories.html", spacecraft=Data.Spacecraft,
                           read=get_profile()["stories"])


# ---------------------------------------------------- Search
@app.route("/search")
def search():
    typed = request.args.get("q", "").strip()
    if typed == "":
        return render_template("search.html", typed="", not_found=False)

    # Same steps as the terminal: exact name, then spelling fix, then Gemini as a last helper.
    corrected = chatbot.Check_title(typed)
    if corrected.lower() == "unknown":
        return render_template("search.html", typed=typed, not_found=True,
                               spacecraft=Data.Spacecraft)

    item = Content_data.find_by_name(corrected)
    if corrected.lower() != typed.lower():
        flash(f"Showing results for {corrected}")
    return redirect(url_for("spacecraft_page", ship_id=item["id"]))


# ---------------------------------------------------- One spacecraft
@app.route("/spacecraft/<ship_id>")
def spacecraft_page(ship_id):
    item = Content_data.find_item(ship_id)
    if item is None:
        abort(404)

    quiz = item["quiz"]
    options = list(enumerate(quiz["options"]))            # [(0, "text"), (1, "text"), ...]
    random.shuffle(options)                               # show the choices in a random order

    return render_template(
        "spacecraft.html",
        item=item,
        already_read=ship_id in get_profile()["stories"],
        quiz_question=quiz["question"],
        quiz_options=options,
    )


@app.route("/spacecraft/<ship_id>/quiz", methods=["POST"])
def spacecraft_quiz(ship_id):
    item = Content_data.find_item(ship_id)
    if item is None:
        abort(404)
    back_to_story = redirect(url_for("spacecraft_page", ship_id=ship_id))

    profile = get_profile()
    if ship_id in profile["stories"]:
        flash("You already finished this story, so there are no new points.")      #for CHALAK public :) 
        return back_to_story

    try:
        picked = int(request.form.get("answer", ""))      # the number of the option picked
    except ValueError:
        flash("Please pick an answer.")
        return back_to_story

    quiz = item["quiz"]
    old_level = tools.get_level(profile["points"])

    gained = Data.POINTS_FOR_NEW_STORY
    if picked == quiz["answer"]:
        flash("Correct!")
        gained += Data.POINTS_FOR_RIGHT_ANSWER
    else:
        flash(f"Not quite. The answer was: {quiz['options'][quiz['answer']]}")

    add_progress(ship_id, gained)
    flash(f"+{gained} points. Total points: {session['points']}")

    new_level = tools.get_level(session["points"])
    if new_level != old_level:
        flash(f"LEVEL UP! You are now a {new_level}.", "levelup")

    return back_to_story


# ---------------------------------------------------- Settings
@app.route("/settings", methods=["GET", "POST"])
def settings():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        error = check_name(name)
        if error is None:
            session["name"] = name
            flash("Name updated.")
            return redirect(url_for("settings"))
    return render_template("settings.html", error=error, max_name=tools.MAX_NAME_LENGTH)


@app.route("/settings/delete", methods=["POST"])
def delete_profile():
    session.clear()                                       # name, points, stories: all gone
    return redirect(url_for("welcome"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


#    The spacecraft page loads at once. Then spacecraft.js asks this route for the
#    slow parts (Wikipedia, NASA, Gemini) and fills them in
# ====================================================================
def get_details(ship_id):
    if ship_id in details_cache:
        return details_cache[ship_id]

    facts, wiki_text, captions, images, sources = fetch_details(ship_id)
    details = {"facts": facts, "wiki_text": wiki_text, "captions": captions,
               "images": images, "sources": sources}
    
    if wiki_text or images:
        details_cache[ship_id] = details
    return details


def split_story(text):
    """Turn the story text into [{"title": "LAUNCH", "text": "..."}, ...] for the page."""
    sections = []
    for line in text.splitlines():
        line = line.strip()
        if line == "":
            continue
        if line.upper() in STORY_TITLES:                  # a title line, e.g. LAUNCH
            sections.append({"title": line.upper(), "text": ""})
            continue
        if not sections:                                  # text that came before any title
            sections.append({"title": "", "text": ""})
        if sections[-1]["text"] != "":
            sections[-1]["text"] += " "
        sections[-1]["text"] += line
    return sections


def pick_image(images):
    """The first NASA picture. (search_spacecraft.fetch_details already collected up to 3.)"""
    if not images:
        return None
    return {"url": images[0]["url"], "title": images[0]["title"]}


@app.route("/api/spacecraft/<ship_id>")
def api_spacecraft(ship_id):
    item = Content_data.find_item(ship_id)
    if item is None:
        abort(404)

    level = tools.get_level(get_profile()["points"])
    details = get_details(ship_id)

    key = (ship_id, level)
    if key not in story_cache:
        story = chatbot.Unique_message(item["name"], level, details["facts"],
                                       details["wiki_text"], details["captions"])
        if story:                                         # only remember real text
            story_cache[key] = story
    story = story_cache.get(key)

    return jsonify({
        "story_ok": story is not None,
        "sections": split_story(story) if story else [],
        "facts": item["facts"],                           # Plan B when Gemini is not available
        "image": pick_image(details["images"]),
        "sources": ["Last Signal archive (key facts)"] + details["sources"],
    })


#_____________________________kioo  ladleee    meawoooooo   :)___________________
if __name__ == "__main__":
    # debug=True automatcly updates the server
    # madarboard  publish er age False  koira dibi :   vulbi na Mahi 
    app.run()
