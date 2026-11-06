import tools
import random
import Data
from Content_data import get_content_List, add_limit
from search_spacecraft import show_picked


def get_story():
    scoreboard = Data.scoreboard()

    # ------------------------------------the story-picker questions-----------
    random.shuffle(Data.Questions)
    for question in Data.Questions:
        tools.clear_screen()
        said_yes = tools.confirm(question["text"])
        if said_yes:
            add_points(scoreboard, question["yes"])
        else:
            add_points(scoreboard, question["no"])

    content_list = get_content_List(top_genre(scoreboard))

    if not content_list:
        print("No spacecraft found for your answers.")
    else:
        while True:
            profile = tools.load_profile()  # reload, so new (read) marks show up
            tools.clear_screen()
            for serial, content in content_list.items():
                mark = "  (read)" if content["id"] in profile["stories"] else ""
                print(f"[{serial}] {content['title']}{mark}")

            print("-------------------------------------------")
            print("To read a story \n Enter the Serial number")
            print("Or Press Enter to return:")
            details = see_details(content_list)
            if details is None:
                break
            show_picked(details)
            tools.enter_to_continue()


def see_details(content_dict):
    while True:
        choice = input("-> ").strip()
        if not choice:
            return None  # Enter = go back

        if not choice.isdigit():
            print("Invalid input: enter a number.")
            continue

        choice = int(choice)
        if choice in content_dict:  # keys are 1..N, however many results came back
            return content_dict[choice]  # the whole item: id, title

        print(f"Invalid input: enter a number from 1 to {len(content_dict)}.")


def add_points(scoreboard, points):
    for genre, point in points.items():
        scoreboard[genre] += point


def top_genre(scoreboard):
    
    ranked_genres = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
    top = []
    for genre, score in ranked_genres:
        if score > 0:
            top.append(genre)

    # Safety: if fewer than 2 tags scored, fill up with the next ones in the ranking
    for genre, score in ranked_genres:
        if len(top) >= 2:
            break
        if genre not in top:
            top.append(genre)

    return top[0], top[1]


if __name__ == "__main__":
    tools.clear_screen()
    print("===================================")
    print(get_story())
    print("===================================")
