"""
Last Signal - Flask web version
===============================
Every spacecraft left behind has one last story.

How this file is organised (top to bottom):
    1. Setup              create the app, the settings and a few small constants
    2. Profile helpers    the visitor's name, points and read stories live in the session
    3. Before every page  a new visitor is first asked for their name
    4. Pages              one function per page (these are the "routes")
    5. The story API      the spacecraft page asks this route for the story and the NASA picture
    6. Start the server

The old terminal files are REUSED, not rewritten:
    Data.py               the spacecraft archive, the questions, the levels
    Content_data.py       find a spacecraft, build the list of matches
    chatbot.py            Gemini: fix a typed name, write the story
    search_spacecraft.py  fetch_details(): Wikipedia text + NASA Image Library pictures
    tools.py              get_level(), points_to_next_level()
    get_story.py          top_genre(), add_points() for the story-picker quiz
"""
import os
import random
from datetime import timedelta

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)

import chatbot
import Content_data
import Data
import tools
from get_story import add_points, top_genre
from icons import icon
from search_spacecraft import fetch_details

# ====================================================================
# 1. SETUP
# ====================================================================
app = Flask(__name__)

# The secret key signs the session cookie so nobody can change it (PDF, Stage 3).
# For a real public website, put a long random value in FLASK_SECRET_KEY.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

# A "permanent" session cookie survives closing the browser, so a visitor is remembered.
app.permanent_session_lifetime = timedelta(days=365)

# Lets every template write {{ icon("search") }}
app.add_template_global(icon)

# Each slide is ONE background and ONE floating object. They sit inside the same
# slide, so when the slide fades in or out, both fade together.
# To pair them differently, or add a fifth pair, just edit this list.
SLIDES = [
    ("bg1.jpg", "object1.webp"),
    ("bg2.jpg", "object2.webp"),
    ("bg3.jpg", "object3.webp"),
    ("bg4.jpg", "object4.webp"),
]

# The five section titles that chatbot.Unique_message asks Gemini to write.
STORY_TITLES = ["LAUNCH", "THE MISSION", "THE END", "WHERE I AM NOW",
                "THE SCIENCE I LEFT BEHIND"]

# Things we already looked up, so the second visit to a page is instant.
details_cache = {}   # spacecraft id          -> Wikipedia text + NASA pictures
story_cache = {}     # (spacecraft id, level) -> the story Gemini wrote


# ====================================================================
# 2. PROFILE HELPERS
#    The terminal version saved the profile in profiles.csv (one person).
#    The web version keeps it in the session cookie (one profile per visitor).
# ====================================================================
def get_profile():
    """The visitor's profile as a dict, or None if they have not told us their name yet."""
    name = session.get("name")
    if not name:
        return None
    return {
        "name": name,
        "points": session.get("points", 0),
        "stories": session.get("stories", []),
    }


def add_progress(story_id, points_gained):
    """Same idea as tools.add_progress, but saved in the session instead of profiles.csv."""
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


# ====================================================================
# 3. BEFORE EVERY PAGE
# ====================================================================
@app.before_request
def ask_new_visitors_for_their_name():
    """Flask runs this before EVERY request. A visitor with no name goes to /welcome first."""
    if request.endpoint in ("welcome", "static"):
        return None                                   # these pages are always allowed
    if request.endpoint is not None and get_profile() is None:
        return redirect(url_for("welcome"))
    return None


@app.context_processor
def add_shared_values():
    """Variables that EVERY template can use (PDF, Stage 3.8)."""
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


# ====================================================================
# 4. PAGES
# ====================================================================
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    """The only thing we ask a new visitor is their name. No knowledge questions."""
    if get_profile() is not None:
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        error = check_name(name)
        if error is None:
            session.permanent = True
            session["name"] = name
            session["points"] = 0              # 0 points = the first level, Explorer
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
    """Text on the left, NASA picture on the right, no menu. The slow parts load afterwards."""
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
    """The 'quick question' after a story. Same points rules as the terminal story_quiz()."""
    item = Content_data.find_item(ship_id)
    if item is None:
        abort(404)
    back_to_story = redirect(url_for("spacecraft_page", ship_id=ship_id))

    profile = get_profile()
    if ship_id in profile["stories"]:
        flash("You already finished this story, so there are no new points.")
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


# ====================================================================
# 5. THE STORY API
#    The spacecraft page loads at once. Then spacecraft.js asks this route for the
#    slow parts (Wikipedia, NASA, Gemini) and fills them in (PDF, Stage 5.6).
# ====================================================================
def get_details(ship_id):
    """Wikipedia text and NASA pictures. They are the same for every level, so cache them."""
    if ship_id in details_cache:
        return details_cache[ship_id]

    facts, wiki_text, captions, images, sources = fetch_details(ship_id)
    details = {"facts": facts, "wiki_text": wiki_text, "captions": captions,
               "images": images, "sources": sources}

    # Do not remember an empty answer (no internet?), so the next visit can try again.
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


# ====================================================================
# 6. START THE SERVER
# ====================================================================
if __name__ == "__main__":
    # debug=True restarts the server when you save a file. Turn it OFF for a public website.
    app.run(debug=True)
