# Last Signal

Every spacecraft left behind has one last story.

A Flask web app for NASA Space Apps 2026, challenge "Abandoned but not Forgotten".
Search a spacecraft, read its story written for your level, and see real NASA images.

**Live demo: https://last-signal-dcs6.onrender.com**

> The first load may take up to a minute while the free server wakes up. Please wait a moment.

## How to try it
1. Enter your name.
2. Search a spacecraft (for example "Spirit"), or use "Find your signal".
3. Read its story, look at the NASA picture, and answer the quick question to earn points and level up.

## Run it on Windows (PowerShell, inside the project folder)

    venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:GEMINI_API_KEY = "paste-your-key-here"
    python app.py

Open http://127.0.0.1:5000

Without a Gemini key the site still works: the story page shows the facts from Data.py instead of an AI story.

## File map

| File | Job |
|---|---|
| app.py | All pages (routes), profile in the session, story API |
| icons.py | The small SVG icons |
| chatbot.py | Gemini code (the client is created only when first used) |
| templates/base.html | Slideshow, gradient, profile icon, Back button, two columns |
| templates/*.html | One file per page |
| static/css/style.css | All styling |
| static/js/ | Slideshow, profile card, story loading |
| static/img/ | 4 backgrounds and 4 floating objects |

## Data sources
Spacecraft text from Wikipedia, spacecraft info from NASA NSSDCA, pictures from the NASA Image and Video Library, stories written by Google Gemini.
