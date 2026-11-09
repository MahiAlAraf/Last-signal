// The background slideshow (PDF, Stage 5.5).
//
// Every ".slide" holds one background and one floating object.
// Every few seconds we move the class "active" to the next slide.
// The CSS does the smooth fade, so this file only does the timing.

const SECONDS_PER_SLIDE = 10; // seconds

const slides = document.querySelectorAll(".slide");
let currentIndex = 0;

function showNextSlide() {
    // 1. hide the current slide (CSS fades it out)
    slides[currentIndex].classList.remove("active");

    // 2. move to the next number, and go back to 0 after the last slide
    currentIndex = currentIndex + 1;
    if (currentIndex >= slides.length) {
        currentIndex = 0;
    }

    // 3. show the new slide (CSS fades it in at the same moment)
    slides[currentIndex].classList.add("active");
}

if (slides.length > 1) {
    setInterval(showNextSlide, SECONDS_PER_SLIDE * 1000);
}
