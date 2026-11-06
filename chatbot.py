import difflib

from google import genai

import Content_data
import Data

Model = "gemini-3.5-flash-lite"
client = genai.Client()


def Check_title(Title):
    """Turn what the user typed into the official name of a spacecraft in the
    archive. Returns "UNKNOWN" if it is not in the archive."""

    # Step 1: exact name or alias (free and instant, no AI needed)
    item = Content_data.find_by_name(Title)
    if item:
        return item["name"]

    # Step 2: small spelling mistakes, like "spirt" -> "Spirit rover" (also free)
    spellings = {}  # every name and alias (lowercase) -> official name
    for entry in Data.Spacecraft:
        spellings[entry["name"].lower()] = entry["name"]
        for alias in entry["aliases"]:
            spellings[alias] = entry["name"]

    close = difflib.get_close_matches(Title.strip().lower(), list(spellings), n=1, cutoff=0.7)
    if close:
        return spellings[close[0]]

    # Step 3: ask Gemini, but only let it choose from OUR list
    names = [entry["name"] for entry in Data.Spacecraft]
    prompt = (
        "The user typed the name of a NASA spacecraft. It may be misspelled or described in other words.\n"
        "Here is the list of spacecraft we have stories for:\n"
        + "\n".join(f"- {name}" for name in names)
        + "\n\nReply with ONLY the exact name from the list that the user means, nothing else.\n"
        "If none of them matches, reply with exactly: UNKNOWN\n\n"
        f"User input: {Title}"
    )
    try:
        Response = client.models.generate_content(model=Model, contents=prompt)
    except Exception as error:
        print(f"(Gemini could not be reached: {error})")
        return "UNKNOWN"

    answer = (Response.text or "").strip().strip(" \"'.").lower()
    for name in names:
        if name.lower() == answer:
            return name  # only accept answers that are really in our list
    return "UNKNOWN"


def Unique_message(Title, Level, Facts, Wiki_text, Captions):
    style = Data.Level_style[Level]

    facts_text = "\n".join(f"- {fact}" for fact in Facts)
    captions_text = "\n".join(f"- {caption}" for caption in Captions)
    if captions_text == "":
        captions_text = "- (none available)"
    if Wiki_text == "":
        Wiki_text = "(not available)"

    prompt = (
        "You are Last Signal, a storyteller who tells the TRUE story of NASA spacecraft that were left behind in space.\n"
        "Write a short story told in the FIRST PERSON, as if the spacecraft itself is speaking to the reader.\n\n"
        "STRICT RULES:\n"
        "1. Use ONLY the information in the FACTS, WIKIPEDIA SUMMARY and NASA CAPTIONS below. "
        "Never invent dates, numbers, names, places or events. If something is not given, leave it out.\n"
        "2. You may describe what the machine might feel, but feelings must never add new facts.\n"
        "3. Include EVERY item from the FACTS list.\n"
        "4. The NASA captions may be about a related topic. Only use a caption if it clearly describes this spacecraft.\n"
        "5. Plain text only. No markdown, no asterisks, no bullet points, no emojis, "
        "and only simple punctuation (no fancy quotes or long dashes).\n"
        "6. Do not write a 'last signal' line. The program adds it.\n\n"
        "STRUCTURE: Use exactly these five section titles, each in capital letters on its own line, in this order:\n"
        "LAUNCH\n"
        "THE MISSION\n"
        "THE END\n"
        "WHERE I AM NOW\n"
        "THE SCIENCE I LEFT BEHIND\n"
        "Write one short paragraph under each title.\n\n"
        f"READER LEVEL: {Level}. {style['description']}\n"
        f"LENGTH: about {style['words']} words in total.\n\n"
        f"SPACECRAFT: {Title}\n\n"
        f"FACTS:\n{facts_text}\n\n"
        f"WIKIPEDIA SUMMARY:\n{Wiki_text}\n\n"
        f"NASA CAPTIONS:\n{captions_text}\n"
    )

    try:
        Responce = client.models.generate_content(model=Model, contents=prompt)
    except Exception as error:
        print(f"(Gemini could not be reached: {error})")
        return None

    text = Responce.text
    if not text:
        return None

    # Safety net: remove markdown symbols if the AI used them anyway
    return text.replace("*", "").replace("#", "").strip()
