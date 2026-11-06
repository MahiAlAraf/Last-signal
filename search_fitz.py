import re
from urllib.parse import quote

import chatbot
import Content_data
import Data
import tools
from Data import raw_review

WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
NASA_SEARCH_URL = "https://images-api.nasa.gov/search"


def search_fitz():
    """User typed a name: correct it, find the id, then show the story."""
    tools.clear_screen()
    user_search = input("\n Search a spacecraft: ").strip()
    if not user_search:
        print("Nothing typed.")
        return

    corrected = chatbot.Check_title(user_search)
    if corrected.lower() == "unknown":
        print("Sorry: that spacecraft is not in the Last Signal archive yet.")
        print("\nStories we have right now:")
        for item in Data.Spacecraft:
            print(f" - {item['name']}")
        return
    if corrected.lower() != user_search.lower():
        print(f"Loading results for {corrected}.....")

    try:
        Media_ID = fetch_id(corrected)
    except ValueError:
        print("Could not find that spacecraft. Try again.")
        return

    show_review(Media_ID, corrected)


def show_picked(item):
    """User picked from the list: we already know the id, so skip Gemini and fetch_id."""
    show_review(item["id"], item["title"])


def show_review(Media_ID, Title):
    profile = tools.load_profile()
    if profile is None:
        print("No profile found. Run main.py to create one.")
        return

    level = tools.get_level(profile["points"])
    item = Content_data.find_item(Media_ID)
    key = (Media_ID, level)

    if key in raw_review:
        responce = raw_review[key]
    else:
        print("\nOpening the archive... the story is being written, please wait.")
        Facts, Wiki_text, Captions, Images, Sources = fetch_details(Media_ID)

        story = chatbot.Unique_message(Title, level, Facts, Wiki_text, Captions)
        if not story:
            print("The AI could not write a story for this spacecraft.")
            return

        responce = {"story": story, "images": Images, "sources": Sources}
        raw_review[key] = responce  # only cache real text

    tools.clear_screen()
    print(f"LAST SIGNAL: {Title}      [Your level: {level}]")
    print("=" * 80)
    tools.print_wrapped(responce["story"])
    if item["last_signal"]:
        print()
        print(f"LAST SIGNAL RECEIVED: {item['last_signal']}")
    print("=" * 80)

    if responce["images"]:
        print("NASA pictures (open the link in your browser):")
        for image in responce["images"]:
            print(f" - {image['title']}")
            print(f"   {image['url']}")
    print("Sources:")
    print(" - Last Signal archive (key facts)")
    for source in responce["sources"]:
        print(f" - {source}")
    print("=" * 80)

    story_quiz(item)


def story_quiz(item):
    """One quick question after a story. This is how the level goes up."""
    profile = tools.load_profile()
    if item["id"] in profile["stories"]:
        print("\nYou already finished this story, so there are no new points.")
        return

    quiz = item["quiz"]
    right_text = quiz["options"][quiz["answer"]]

    print("\nQuick question to check what you learned:\n")
    old_level = tools.get_level(profile["points"])
    got_it = tools.ask_quiz(quiz["question"], quiz["options"], quiz["answer"])

    gained = Data.POINTS_FOR_NEW_STORY
    if got_it:
        print("\nCorrect!")
        gained += Data.POINTS_FOR_RIGHT_ANSWER
    else:
        print(f"\nNot quite. The answer was: {right_text}")

    tools.add_progress(profile, item["id"], gained)
    new_level = tools.get_level(profile["points"])

    print(f"+{gained} points. Total points: {profile['points']}")
    if new_level != old_level:
        print(f"\n*** LEVEL UP! You are now a {new_level}. ***")


def fetch_id(Title):
    item = Content_data.find_by_name(Title)
    if item is None:
        raise ValueError("Spacecraft not found in the archive")
    return item["id"]


def clean_text(text, limit=400):
    """NASA captions can contain HTML and be very long. Clean and shorten them."""
    text = re.sub(r"<[^>]+>", " ", text)  # remove html tags
    text = re.sub(r"\s+", " ", text).strip()  # remove extra spaces and new lines
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def fetch_details(ID):
    item = Content_data.find_item(ID)
    Facts = item["facts"]  # our own facts always work, even with no internet
    Sources = []

    # ---------------------------Wikipedia summary---------------------------
    Wiki_text = ""
    wiki_title = item["wiki"].replace(" ", "_")
    wiki_url = WIKIPEDIA_SUMMARY_URL + quote(wiki_title, safe="")
    wiki_data = Content_data.responce(
        wiki_url, headers={"User-Agent": Content_data.USER_AGENT}
    )
    if wiki_data:
        Wiki_text = clean_text(wiki_data.get("extract", ""), limit=1500)
        page_url = wiki_data.get("content_urls", {}).get("desktop", {}).get("page", "")
        if Wiki_text:
            Sources.append(f"Wikipedia, '{item['wiki']}' (CC BY-SA) {page_url}".strip())

    # ----------------------NASA Image and Video Library---------------------
    Captions = []
    Images = []
    nasa_data = Content_data.responce(
        NASA_SEARCH_URL,
        params={"q": item["nasa_query"], "media_type": "image", "page_size": 5},
    )
    if nasa_data:
        entries = nasa_data.get("collection", {}).get("items", [])
        for entry in entries[:3]:
            info = (entry.get("data") or [{}])[0]
            links = entry.get("links") or [{}]
            image_url = links[0].get("href", "")
            title = info.get("title", "NASA image")
            caption = clean_text(info.get("description", ""))

            if caption:
                Captions.append(caption)
            if image_url:
                Images.append({"title": title, "url": image_url})
        if Images:
            Sources.append("NASA Image and Video Library (images.nasa.gov)")

    return Facts, Wiki_text, Captions, Images, Sources


if __name__ == "__main__":
    search_fitz()
