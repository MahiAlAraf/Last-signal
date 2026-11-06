import requests

import Data

add_limit = 6

# Wikipedia asks every program to say who it is in the User-Agent header.
USER_AGENT = "LastSignal/0.1 (student hackathon project; github.com/MahiAlAraf/Fitz)"


def find_by_name(text):
    """Look for a spacecraft by its name or one of its aliases (ignores case).
    Returns the archive item, or None."""
    wanted = text.strip().lower()
    for item in Data.Spacecraft:
        if item["name"].lower() == wanted:
            return item
        if wanted in item["aliases"]:
            return item
    return None


def find_item(Media_ID):
    """Look for a spacecraft by its id. Returns the archive item, or None."""
    for item in Data.Spacecraft:
        if item["id"] == Media_ID:
            return item
    return None


def get_content_List(genres_Tuple):
    # The "tags" are the new genres: Moon, Mars, Rover, Survival ...
    top_tag, second_tag = genres_Tuple

    has_both = []  # spacecraft that have BOTH tags (best matches)
    has_one = []  # spacecraft that have only ONE of the tags

    for item in Data.Spacecraft:
        has_top = top_tag in item["tags"]
        has_second = second_tag in item["tags"]

        if has_top and has_second:
            has_both.append(item)
        elif has_top:
            has_one.append((0, item))  # 0 = matches the top tag, goes first
        elif has_second:
            has_one.append((1, item))

    has_one.sort(key=lambda pair: pair[0])  # stable: keeps archive order inside a group
    extra_items = [item for _, item in has_one]

    return ContentList_Dict(has_both, extra_items)


def get_title(item):
    return item["name"]


def ContentList_Dict(Main_data_package, Sub_Package=None):
    content_info = {}
    seen_ids = set()  # ids already in the list
    slot = 1  # next free number in the list

    # 1) best matches first: spacecraft that have BOTH tags
    for item in Main_data_package:
        if slot > add_limit:
            break
        content_info[slot] = {"id": item["id"], "title": get_title(item)}
        seen_ids.add(item["id"])
        slot += 1

    # 2) fill the remaining slots from the ONE-tag matches, skipping duplicates
    if Sub_Package:
        for item in Sub_Package:
            if slot > add_limit:
                break
            if item["id"] in seen_ids:
                continue  # already listed, do not use a slot
            content_info[slot] = {"id": item["id"], "title": get_title(item)}
            seen_ids.add(item["id"])
            slot += 1

    return content_info


def responce(URL, params=None, headers=None):
    try:
        content_responce = requests.get(URL, params=params, headers=headers, timeout=10)
        content_responce.raise_for_status()  # errors on 404, 500...
        return content_responce.json()
    except (requests.exceptions.RequestException, ValueError):
        return None  # network error OR response was not valid JSON


def main():
    for item in Data.Spacecraft:
        print(item["id"], "-", item["name"], item["tags"])
    print(get_content_List(("Mars", "Rover")))


if __name__ == "__main__":
    main()
