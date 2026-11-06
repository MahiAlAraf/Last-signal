# ----------------------------- 1. Levels ----------------------------------
# (level name, minimum points). Keep sorted from lowest to highest.
Levels = [("Explorer", 0), ("Navigator", 4), ("Commander", 12)]

POINTS_FOR_NEW_STORY = 1  # reading a story you never read before
POINTS_FOR_RIGHT_ANSWER = 2  # answering that story's quick question correctly

# How the AI should write for each level.
Level_style = {
    "Explorer": {
        "words": 180,
        "description": (
            "The reader is a curious child of about 8 to 11 who knows very little "
            "about space. Use short, simple sentences. Avoid jargon. If you must use "
            "a space word, explain it right away with an everyday comparison."
        ),
    },
    "Navigator": {
        "words": 250,
        "description": (
            "The reader is a teenager who knows some space basics. Use clear, plain "
            "language. You may use a few space words, but explain each one briefly "
            "the first time."
        ),
    },
    "Commander": {
        "words": 330,
        "description": (
            "The reader already knows a lot about space missions. You may use "
            "technical terms that appear in the facts and include the precise "
            "numbers from the facts."
        ),
    },
}

# ------------------------- 2. Starter questions ---------------------------
Starter_questions = [
    {
        "text": "What is a rover?",
        "options": [
            "A vehicle that drives around on another world",
            "A type of rocket engine",
            "A telescope that orbits Earth",
        ],
        "answer": 0,
    },
    {
        "text": "About how long does a radio signal take to travel one way between Mars and Earth?",
        "options": [
            "A few seconds",
            "Between about 3 and 22 minutes",
            "About two days",
        ],
        "answer": 1,
    },
    {
        "text": "Which NASA program landed astronauts on the Moon between 1969 and 1972?",
        "options": ["Voyager", "Apollo", "Viking"],
        "answer": 1,
    },
]


# ------------------------ 3. Story-picker quiz ----------------------------
def scoreboard():
    return {
        # ---- where ----
        "Moon": 0,
        "Mars": 0,
        "Deep Space": 0,
        # ---- what kind of machine ----
        "Rover": 0,
        "Lander": 0,
        # ---- what kind of story ----
        "Survival": 0,
        "Discovery": 0,
        "Firsts": 0,
        "Humans": 0,
    }


Questions = [
    {  # 1. Place
        "text": "Would you rather visit a place where humans have already walked?",
        "yes": {"Moon": 3, "Humans": 2},
        "no": {"Mars": 2, "Deep Space": 2},
    },
    {  # 2. Machine
        "text": "Do you like machines that drive around on their own wheels?",
        "yes": {"Rover": 3, "Mars": 1},
        "no": {"Lander": 2, "Deep Space": 1},
    },
    {  # 3. Struggle
        "text": "Do you enjoy stories about a machine fighting to survive dust, cold or darkness?",
        "yes": {"Survival": 3, "Mars": 1},
        "no": {"Discovery": 2, "Firsts": 1},
    },
    {  # 4. Records
        "text": "Do you get excited about 'first ever' records?",
        "yes": {"Firsts": 3, "Deep Space": 1},
        "no": {"Discovery": 2, "Humans": 1},
    },
    {  # 5. Science
        "text": "Do you want to hear about big scientific discoveries?",
        "yes": {"Discovery": 3, "Lander": 1},
        "no": {"Survival": 1, "Humans": 2},
    },
]


# ------------------------- 4. Spacecraft archive --------------------------
# Every item:
#   id           short unique name used inside the program
#   name         the name shown to the user
#   aliases      other names the user might type (lowercase)
#   tags         must be names from scoreboard()
#   wiki         exact Wikipedia page title (used to fetch a summary)
#   nasa_query   search words for the NASA Image and Video Library
#   facts        the facts the AI MUST use (the AI may not invent others)
#   last_signal  text printed after "LAST SIGNAL RECEIVED:" (None = skip line)
#   quiz         one question about the facts, "answer" = index in "options"
Spacecraft = [
    {
        "id": "spirit",
        "name": "Spirit rover",
        "aliases": ["spirit", "mer-a", "mars exploration rover spirit"],
        "tags": ["Mars", "Rover", "Survival", "Discovery"],
        "wiki": "Spirit (rover)",
        "nasa_query": "Spirit rover Mars Exploration Rover",
        "facts": [
            "Spirit launched on June 10, 2003 and landed on Mars on January 4, 2004, inside Gusev Crater.",
            "Its planned mission was 90 Martian days (sols), but it kept working for more than six years.",
            "In 2009 it got stuck in soft sand and could not drive out.",
            "Its last message to Earth came on March 22, 2010, and NASA ended its recovery attempts on May 25, 2011.",
            "It found bright, silica-rich soil, which scientists think formed near hot springs or steam vents, a sign that water once existed there.",
            "Spirit still sits on Mars in Gusev Crater.",
        ],
        "last_signal": "March 22, 2010",
        "quiz": {
            "question": "What stopped Spirit from driving in 2009?",
            "options": [
                "It got stuck in soft sand",
                "It fell off a cliff",
                "It ran out of wheels to turn",
            ],
            "answer": 0,
        },
    },
    {
        "id": "opportunity",
        "name": "Opportunity rover",
        "aliases": ["opportunity", "oppy", "mer-b", "mars exploration rover opportunity"],
        "tags": ["Mars", "Rover", "Survival", "Discovery"],
        "wiki": "Opportunity (rover)",
        "nasa_query": "Opportunity rover Meridiani Planum",
        "facts": [
            "Opportunity launched on July 7, 2003 and landed on Mars on January 25, 2004, at Meridiani Planum.",
            "It was built for a 90-sol mission but worked for more than 14 years.",
            "It drove about 45 kilometers (28 miles), farther than a marathon.",
            "A huge dust storm covered Mars in 2018 and blocked sunlight from its solar panels. Its last message came on June 10, 2018, and NASA declared the mission over on February 13, 2019.",
            "It found small round rocks rich in hematite, nicknamed blueberries, and proof that liquid water once soaked the ground there.",
            "Opportunity still sits on Mars.",
        ],
        "last_signal": "June 10, 2018",
        "quiz": {
            "question": "What blocked sunlight from Opportunity's solar panels in 2018?",
            "options": [
                "A huge dust storm",
                "A fallen rock",
                "A broken antenna",
            ],
            "answer": 0,
        },
    },
    {
        "id": "sojourner",
        "name": "Sojourner rover",
        "aliases": ["sojourner", "mars pathfinder", "pathfinder"],
        "tags": ["Mars", "Rover", "Firsts", "Discovery"],
        "wiki": "Sojourner (rover)",
        "nasa_query": "Sojourner rover Mars Pathfinder",
        "facts": [
            "Sojourner was the first rover to drive on Mars. It arrived on July 4, 1997, riding on the Mars Pathfinder lander, and landed in Ares Vallis.",
            "It was about the size of a microwave oven.",
            "It was planned to work for 7 sols (Martian days) and worked for 83.",
            "The last signal from the Pathfinder lander came on September 27, 1997.",
            "The lander was later renamed the Carl Sagan Memorial Station.",
            "Sojourner and Pathfinder still sit on Mars.",
        ],
        "last_signal": "September 27, 1997 (from the Pathfinder lander)",
        "quiz": {
            "question": "How long was Sojourner planned to work?",
            "options": [
                "7 Martian days (sols)",
                "90 Martian days (sols)",
                "Two Earth years",
            ],
            "answer": 0,
        },
    },
    {
        "id": "ingenuity",
        "name": "Ingenuity helicopter",
        "aliases": ["ingenuity", "mars helicopter", "ingenuity mars helicopter"],
        "tags": ["Mars", "Firsts"],
        "wiki": "Ingenuity (helicopter)",
        "nasa_query": "Ingenuity Mars helicopter",
        "facts": [
            "Ingenuity was a small helicopter that traveled to Mars attached to the Perseverance rover. It landed on February 18, 2021.",
            "On April 19, 2021 it made the first powered, controlled flight on another planet.",
            "It was planned to fly 5 times, but it flew 72 times.",
            "Its final flight was on January 18, 2024. A rotor blade was damaged, and NASA ended the mission on January 25, 2024.",
            "Ingenuity rests in Jezero Crater on Mars.",
        ],
        "last_signal": "January 18, 2024 (its 72nd and final flight)",
        "quiz": {
            "question": "About how many flights did Ingenuity actually make?",
            "options": ["5", "72", "300"],
            "answer": 1,
        },
    },
    {
        "id": "phoenix",
        "name": "Phoenix lander",
        "aliases": ["phoenix", "phoenix mars lander"],
        "tags": ["Mars", "Lander", "Survival", "Discovery"],
        "wiki": "Phoenix (spacecraft)",
        "nasa_query": "Phoenix Mars lander",
        "facts": [
            "Phoenix landed near the north pole of Mars on May 25, 2008.",
            "It dug into the soil with a robotic arm and confirmed that there was water ice just under the surface.",
            "It was planned to work for about three months and worked for about five.",
            "As the dark polar winter came, sunlight faded and its solar panels could no longer power it. Its last contact was on November 2, 2008.",
            "Phoenix still sits in the Martian arctic.",
        ],
        "last_signal": "November 2, 2008",
        "quiz": {
            "question": "What did Phoenix find under the Martian soil?",
            "options": ["Water ice", "Living plants", "Old metal tools"],
            "answer": 0,
        },
    },
    {
        "id": "viking1",
        "name": "Viking 1 lander",
        "aliases": ["viking", "viking 1", "viking lander", "viking 1 lander"],
        "tags": ["Mars", "Lander", "Discovery"],
        "wiki": "Viking 1",
        "nasa_query": "Viking 1 lander Mars Chryse Planitia",
        "facts": [
            "The Viking 1 lander touched down on Mars on July 20, 1976, on a plain called Chryse Planitia.",
            "It carried experiments that searched for signs of life in the Martian soil. The results were not clear and are still debated.",
            "It was planned to work for 90 days but worked for more than six years.",
            "Contact was lost on November 11, 1982, after a command error from Earth, and NASA never heard from it again.",
            "The lander was later renamed the Thomas A. Mutch Memorial Station.",
            "It still sits on Mars.",
        ],
        "last_signal": "November 11, 1982",
        "quiz": {
            "question": "What did Viking 1's experiments search for in the Martian soil?",
            "options": ["Signs of life", "Gold", "Diamonds"],
            "answer": 0,
        },
    },
    {
        "id": "insight",
        "name": "InSight lander",
        "aliases": ["insight", "mars insight"],
        "tags": ["Mars", "Lander", "Survival", "Discovery"],
        "wiki": "InSight",
        "nasa_query": "InSight Mars lander",
        "facts": [
            "InSight landed on Mars on November 26, 2018, on a flat plain called Elysium Planitia.",
            "It carried a seismometer and recorded more than 1,300 marsquakes.",
            "Its measurements helped scientists learn about the size and layers inside Mars: the crust, the mantle and the core.",
            "Dust slowly covered its solar panels until it could not make enough power. In 2022 it sent a final selfie showing the dust, and NASA declared the mission over on December 21, 2022.",
            "InSight still sits on Mars.",
        ],
        "last_signal": "December 2022 (mission declared over on December 21, 2022)",
        "quiz": {
            "question": "What did InSight record more than 1,300 of?",
            "options": ["Marsquakes", "Dust storms", "Rock samples"],
            "answer": 0,
        },
    },
    {
        "id": "lrv",
        "name": "Apollo Lunar Roving Vehicle",
        "aliases": ["lrv", "lunar rover", "moon buggy", "apollo rover", "lunar roving vehicle"],
        "tags": ["Moon", "Rover", "Humans"],
        "wiki": "Lunar Roving Vehicle",
        "nasa_query": "Lunar Roving Vehicle Apollo",
        "facts": [
            "Three Lunar Roving Vehicles were driven on the Moon, on Apollo 15, 16 and 17, in 1971 and 1972.",
            "Each one was folded up inside the lunar module, unfolded on the Moon, and ran on batteries.",
            "They let astronauts travel several kilometers from the lander to collect rocks.",
            "A TV camera on each rover was aimed by controllers on Earth to film the astronauts' ascent stage lifting off from the Moon.",
            "When the astronauts went home, all three rovers were left behind, and they still sit on the Moon.",
        ],
        "last_signal": "December 14, 1972 (Apollo 17 lifted off, the last time people were on the Moon)",
        "quiz": {
            "question": "On which Apollo missions were rovers driven on the Moon?",
            "options": [
                "Apollo 15, 16 and 17",
                "Apollo 11, 12 and 13",
                "Apollo 7, 8 and 9",
            ],
            "answer": 0,
        },
    },
    {
        "id": "alsep",
        "name": "Apollo Lunar Surface Experiments Package (ALSEP)",
        "aliases": ["alsep", "apollo moon experiments", "apollo lunar surface experiments package"],
        "tags": ["Moon", "Humans", "Discovery"],
        "wiki": "Apollo Lunar Surface Experiments Package",
        "nasa_query": "Apollo Lunar Surface Experiments Package ALSEP",
        "facts": [
            "ALSEP stands for Apollo Lunar Surface Experiments Package. Astronauts set up these science stations on the Moon on Apollo 12, 14, 15, 16 and 17.",
            "They were powered by small nuclear generators and sent data to Earth for years.",
            "They measured moonquakes and heat coming from inside the Moon, among other things.",
            "NASA switched them off by command on September 30, 1977, to save money.",
            "The stations still sit on the Moon where the astronauts left them.",
        ],
        "last_signal": "September 30, 1977 (switched off by NASA)",
        "quiz": {
            "question": "How did the ALSEP stations get their power?",
            "options": [
                "Small nuclear generators",
                "Wind turbines",
                "Batteries charged by astronauts",
            ],
            "answer": 0,
        },
    },
    {
        "id": "surveyor3",
        "name": "Surveyor 3 lander",
        "aliases": ["surveyor", "surveyor 3"],
        "tags": ["Moon", "Lander", "Humans"],
        "wiki": "Surveyor 3",
        "nasa_query": "Surveyor 3 lunar lander",
        "facts": [
            "Surveyor 3 landed on the Moon on April 20, 1967, in a region called Oceanus Procellarum, the Ocean of Storms.",
            "It had a camera and a robotic scoop to test the Moon's soil, which helped NASA see that the surface was firm enough for astronauts.",
            "In November 1969, Apollo 12 astronauts Pete Conrad and Alan Bean landed about 180 meters (600 feet) away and walked to it.",
            "They cut off parts, including its TV camera, and brought them back to Earth so scientists could study how materials survived on the Moon.",
            "The rest of Surveyor 3 still sits on the Moon.",
        ],
        "last_signal": None,
        "quiz": {
            "question": "What did the Apollo 12 astronauts bring back from Surveyor 3?",
            "options": [
                "Its TV camera and other parts",
                "The whole lander",
                "A rock it had collected",
            ],
            "answer": 0,
        },
    },
    {
        "id": "pioneer10",
        "name": "Pioneer 10 probe",
        "aliases": ["pioneer", "pioneer 10"],
        "tags": ["Deep Space", "Firsts", "Discovery"],
        "wiki": "Pioneer 10",
        "nasa_query": "Pioneer 10 spacecraft",
        "facts": [
            "Pioneer 10 launched on March 2, 1972. It was the first spacecraft to cross the asteroid belt and the first to fly past Jupiter, in December 1973.",
            "It carries a metal plaque that shows humans and where Earth is, in case anyone ever finds it.",
            "It was built to work for 21 months but kept sending signals for about 30 years.",
            "Its last signal came on January 23, 2003, when it was more than 10 billion kilometers from Earth.",
            "It is heading toward the star Aldebaran, but it will take more than 2 million years to get there.",
        ],
        "last_signal": "January 23, 2003",
        "quiz": {
            "question": "How does Pioneer 10 carry a message for anyone who finds it?",
            "options": [
                "A metal plaque",
                "A song played on repeat",
                "A painted flag",
            ],
            "answer": 0,
        },
    },
    {
        "id": "kepler",
        "name": "Kepler Space Telescope",
        "aliases": ["kepler", "kepler telescope", "kepler space telescope"],
        "tags": ["Deep Space", "Discovery"],
        "wiki": "Kepler space telescope",
        "nasa_query": "Kepler space telescope exoplanets",
        "facts": [
            "Kepler launched on March 7, 2009 to hunt for planets around other stars.",
            "It stared at one patch of sky and watched for tiny dips in starlight when a planet crossed in front of a star.",
            "It helped find more than 2,600 confirmed planets and showed that planets are common around stars.",
            "It ran out of fuel, and NASA retired it on October 30, 2018. It was left in orbit around the Sun, trailing behind Earth.",
        ],
        "last_signal": "October 30, 2018 (NASA retired it)",
        "quiz": {
            "question": "What did Kepler hunt for?",
            "options": [
                "Planets around other stars",
                "Asteroids that might hit Earth",
                "Water on the Moon",
            ],
            "answer": 0,
        },
    },
]

# Stories already written this session, so we do not ask the AI twice.
# key = (spacecraft id, level)  ->  {"story": text, "images": [...], "sources": [...]}
raw_review = {}
