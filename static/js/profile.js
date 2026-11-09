// The profile card opens when you click the profile icon (the HTML <details> tag does that).
// This file only adds two extras: close the card when you click anywhere else, or press Escape.

const profile = document.querySelector("details.profile");

if (profile) {
    document.addEventListener("click", function (event) {
        if (!profile.contains(event.target)) {
            profile.open = false;
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            profile.open = false;
        }
    });
}
