import sys
import random
import cowsay
import tools
import Data
from search_fitz import search_fitz
from get_fitz import get_fitz

MENU_EXIT = "exit"
MENU_PROFILE_DELETED = "profile_deleted"


def main():
    while True:
        tools.clear_screen()

        profile = tools.load_profile()
        if profile is None:

            profile = create_profile()
            tools.clear_screen()

        greetings(profile)

        if show_menu() == MENU_EXIT:
            print("Exiting the program. Goodbye!")
            sys.exit(0)
        else:
            continue


def create_profile():
    print("Welcome to LAST SIGNAL !")
    print("Every spacecraft left behind has one last story.")
    print("==================================")
    name = tools.ask_name()
    points = starter_check()

    tools.clear_screen()
    print("==================================")
    print(f"\nProfile Created:\nName: {name}\nLevel: {tools.get_level(points)}\n")
    print("==================================")

    tools.save_profile(name, points)
    tools.enter_to_continue(name=name.split(" ")[0].title())
    return tools.load_profile()


def starter_check():
    """Three quick questions. They set the first level (no age needed)."""
    tools.clear_screen()
    print("Three quick questions help Last Signal pick your starting level.")
    print("Not sure about an answer? Just guess. Nothing is lost.")
    tools.enter_to_continue()

    points = 0
    for question in Data.Starter_questions:
        tools.clear_screen()
        right = tools.ask_quiz(question["text"], question["options"], question["answer"])
        if right:
            points += Data.POINTS_FOR_RIGHT_ANSWER
    return points


def show_menu():
    while True:
        tools.clear_screen()
        print("+--------------------------------------+")
        print("|         [1] Search a spacecraft      |")
        print("|         [2] Find your signal         |")
        print("|         [3] Show profile             |")
        print("|         [4] Exit                     |")
        print("+--------------------------------------+")
        user_choice = tools.choice(1, 4)

        if user_choice == 1:
            search_fitz()
            tools.enter_to_continue()
        elif user_choice == 2:
            print("==================================")
            get_fitz()
            print("==================================")
            tools.enter_to_continue()
        elif user_choice == 3:
            if show_profile() == MENU_PROFILE_DELETED:
                return MENU_PROFILE_DELETED
        elif user_choice == 4:
            return MENU_EXIT


def greetings(profile):
    animals = [
        "cow",
        "daemon",
        "dragon",
        "fox",
        "ghostbusters",
        "kitty",
        "meow",
        "miki",
        "octopus",
        "stegosaurus",
        "stimpy",
        "trex",
        "turkey",
        "turtle",
        "tux",
    ]
    selected_animal = random.choice(animals)
    print(cowsay.get_output_string(selected_animal, f"Hello {profile['name']}!"))
    tools.enter_to_continue(name=profile["name"].split(" ")[0].title())


def show_profile():
    tools.clear_screen()

    profile = tools.load_profile()
    if profile is None:
        print("No profile found.")
        tools.enter_to_continue()
        return MENU_PROFILE_DELETED

    print("===================================")
    print("Name   :", profile["name"])
    print("Level  :", tools.get_level(profile["points"]))
    print("Points :", profile["points"])
    print("Stories:", f"{len(profile['stories'])} of {len(Data.Spacecraft)} read")

    next_level = tools.points_to_next_level(profile["points"])
    if next_level is not None:
        name, needed = next_level
        print(f"Next level: {name} (in {needed} more points)")
    else:
        print("Next level: you are at the top level!")
    print("===================================")

    print("\n\n[1] to DELETE profile")
    print("Press Enter to go back to the main menu")

    if input("> ").strip() == "1":
        if tools.confirm("Delete your profile? This cannot be undone."):
            tools.delete_profile()
            print("Profile deleted.")
            tools.enter_to_continue()
            return MENU_PROFILE_DELETED

    return None


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting the program. Goodbye!")
        sys.exit(0)
