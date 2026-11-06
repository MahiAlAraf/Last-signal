import csv
import os
import random
import textwrap

import Data

PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles.csv")
PROFILE_FIELDS = ["name", "points", "stories"]
STORY_SEPARATOR = ";"  # stories are saved in one cell, like: spirit;kepler

MAX_NAME_LENGTH = 50


def clear_screen():
    # Executes 'cls' on Windows, 'clear' on Linux and Mac
    os.system("cls" if os.name == "nt" else "clear")


def choice(low, high):
    """Keep asking until the user types a whole number from low to high."""
    while True:
        try:
            user_input = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if low <= user_input <= high:
            return user_input
        print(f"Please enter a number between {low} and {high}.")


def enter_to_continue(name=""):
    print()
    input(f"Press Enter to continue {name}...")


def confirm(question):
   
    while True:
        print("=====================================================")
        answer = input(f"{question} [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Invalid input. Please enter 'y' or 'n'.")


def ask_quiz(question, options, answer_index):
    
    right_text = options[answer_index]
    shuffled = list(options)  # copy, so the original list keeps its order
    random.shuffle(shuffled)

    print(question)
    print()
    for number, text in enumerate(shuffled, start=1):
        print(f"  [{number}] {text}")
    print()

    picked = choice(1, len(shuffled))
    return shuffled[picked - 1] == right_text


def print_wrapped(text, width=78):
    """Print text so long lines break nicely in the terminal.
    Blank lines (paragraph breaks) are kept."""
    for line in text.splitlines():
        if line.strip() == "":
            print()
        else:
            print(textwrap.fill(line.strip(), width=width))


def ask_name():
    while True:
        name = input("Enter your name: ").strip()

        if name == "":
            print("Name cannot be empty. Please try again.")
        elif len(name) > MAX_NAME_LENGTH:
            print(
                f"Name is too long (max {MAX_NAME_LENGTH} characters). Please try again."
            )
        else:
            return name


# --------------------------- knowledge level ------------------------------
def get_level(points):
    
    level_name = Data.Levels[0][0]
    for name, minimum in Data.Levels:
        if points >= minimum:
            level_name = name
    return level_name


def points_to_next_level(points):
    """Returns (next level name, points still needed) or None at the top."""
    for name, minimum in Data.Levels:
        if points < minimum:
            return name, minimum - points
    return None


# ------------------------------- profile ----------------------------------
def save_profile(name, points=0, stories=None):
    if stories is None:
        stories = []

    with open(PROFILE_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=PROFILE_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "name": name,
                "points": points,
                "stories": STORY_SEPARATOR.join(stories),
            }
        )


def load_profile():

    if not os.path.exists(PROFILE_PATH):
        return None

    try:
        with open(PROFILE_PATH, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            row = next(reader, None)  # None when the file has no data row
    except (OSError, UnicodeDecodeError, csv.Error):
        return None

    if row is None:
        return None

    # name and points must be filled in. (stories may be empty for a new user.)
    # An old Fitz profile file has no "points" column, so it counts as missing.
    for field in ("name", "points"):
        if not row.get(field):
            return None

    try:
        row["points"] = int(row["points"])
    except ValueError:
        return None

    if row["points"] < 0:
        return None

    stories_text = row.get("stories") or ""
    row["stories"] = [story for story in stories_text.split(STORY_SEPARATOR) if story]

    return row


def add_progress(profile, story_id, points_gained):
    """Add points, remember the story as read, and save the profile."""
    profile["points"] += points_gained
    if story_id not in profile["stories"]:
        profile["stories"].append(story_id)
    save_profile(profile["name"], profile["points"], profile["stories"])


def delete_profile():
    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)
