// The spacecraft page (PDF, Stage 5.6).
//
// The page itself appears at once with "Receiving signal...".
// This file then asks the server for the slow parts (story, NASA picture, sources)
// and fills them in when the answer arrives.

const storyBox = document.querySelector("#story");
const sourcesBox = document.querySelector("#sources");
const imageBox = document.querySelector("#image-box");
const quizBox = document.querySelector("#quiz");


// A small helper: make a tag that holds some text.
// textContent is safe: it shows text as text and never runs it as HTML.
function makeElement(tag, text, className) {
    const element = document.createElement(tag);
    element.textContent = text;
    if (className) {
        element.className = className;
    }
    return element;
}


function showStory(data) {
    storyBox.textContent = "";                 // remove "Receiving signal..."

    if (data.story_ok) {
        data.sections.forEach(function (section) {
            if (section.title) {
                storyBox.appendChild(makeElement("h3", section.title));
            }
            storyBox.appendChild(makeElement("p", section.text));
        });
        return;
    }

    // Plan B: the AI storyteller could not be reached, so show the facts we already have.
    storyBox.appendChild(makeElement(
        "p",
        "The AI storyteller could not be reached right now, " +
        "so here are the facts from the Last Signal archive.",
        "note"
    ));
    const list = document.createElement("ul");
    data.facts.forEach(function (fact) {
        list.appendChild(makeElement("li", fact));
    });
    storyBox.appendChild(list);
}


function showImage(image) {
    imageBox.textContent = "";                 // remove the pulsing "Searching..." message

    if (!image) {
        imageBox.appendChild(makeElement("p", "No NASA picture was found for this one.", "muted"));
        return;
    }

    const picture = document.createElement("img");
    picture.alt = image.title;
    picture.onload = function () {
        picture.classList.add("loaded");       // the CSS fades it in
    };
    picture.onerror = function () {
        imageBox.textContent = "The NASA picture could not be loaded.";
    };
    picture.src = image.url;

    imageBox.appendChild(picture);
    imageBox.appendChild(makeElement(
        "figcaption",
        image.title + "  |  Image: NASA Image and Video Library"
    ));
}


function showSources(sources) {
    sourcesBox.appendChild(makeElement("p", "Sources:"));
    sources.forEach(function (source) {
        sourcesBox.appendChild(makeElement("p", "- " + source));
    });
}


async function loadSpacecraft() {
    try {
        const response = await fetch(storyBox.dataset.url);
        if (!response.ok) {
            throw new Error("The server answered with status " + response.status);
        }
        const data = await response.json();

        showStory(data);
        showImage(data.image);
        showSources(data.sources);
    } catch (error) {
        storyBox.textContent = "The signal was lost. Please reload the page to try again.";
        imageBox.textContent = "";
    }

    quizBox.hidden = false;                    // show the quick question either way
}


loadSpacecraft();
