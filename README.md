# Last Signal (web version)

A Flask website adapted from the terminal version of Last Signal.
NASA Space Apps 2026: "Abandoned but not Forgotten".

## Run it on Windows (PowerShell, inside the project folder)

```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY = "paste-your-key-here"
python app.py
```

Open http://127.0.0.1:5000

Without a Gemini key the site still works: the story page shows the facts
from Data.py instead of an AI story.

## Polaris font

Copy the font file into `static/fonts/` as `Polaris.otf`, `Polaris.ttf` or `Polaris.woff2`.
See `static/fonts/README.txt`. Check the font's licence first.

## File map

| File | Job |
|---|---|
| app.py | All pages (routes), profile in the session, story API |
| icons.py | The small SVG icons |
| chatbot.py | Your Gemini code (changed: the client is created only when first used) |
| templates/base.html | Slideshow, gradient, profile icon, Back button, two columns |
| templates/*.html | One file per page, each fills the blocks of base.html |
| static/css/style.css | All styling, in numbered sections |
| static/js/slideshow.js | Changes the slide every 5 seconds |
| static/js/profile.js | Closes the profile card on outside click or Escape |
| static/js/spacecraft.js | Loads story + NASA picture after the page appears |
| static/img/ | bg1-4.jpg and object1-4.webp |

## Change which background goes with which object

Open `app.py` and edit the `SLIDES` list. Each pair is (background, object).

## Differences from the terminal version

- Profiles live in the browser's session cookie, so `profiles.csv` is not used.
- The starter knowledge-level questions are gone. A new visitor only gives a name
  and starts at Explorer with 0 points.
- Points rules are the same: +1 for a new story, +2 for a correct quick question.
- Set `FLASK_SECRET_KEY` to a long random text before putting the site online.
