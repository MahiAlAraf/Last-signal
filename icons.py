"""
Tiny inline SVG icons, so the website needs no icon library.

In a template, write:   {{ icon("search") }}
The icon takes the colour of the text around it (stroke="currentColor"),
so when a menu link turns amber on hover, its icon turns amber too.
"""
from markupsafe import Markup

ICON_PATHS = {
    # a globe
    "home": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/>'
            '<path d="M3 12h18"/>',
    # two sparkles
    "find": '<path d="M11 3l1.9 5.1L18 10l-5.1 1.9L11 17l-1.9-5.1L4 10l5.1-1.9z"/>'
            '<path d="M18.5 15l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    # a rocket
    "stories": '<path d="M12 2c3.2 2.2 5 5.6 5 9.5L15 15H9l-2-3.5C7 7.6 8.8 4.2 12 2z"/>'
               '<circle cx="12" cy="9" r="1.6"/>'
               '<path d="M7.2 12.5L4 16l1 3 3-1M16.8 12.5L20 16l-1 3-3-1M10 18l2 4 2-4"/>',
    # a cog
    "settings": '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="6.5"/>'
                '<path d="M12 2v3.5M12 18.5V22M2 12h3.5M18.5 12H22M4.9 4.9l2.5 2.5'
                'M16.6 16.6l2.5 2.5M4.9 19.1l2.5-2.5M16.6 7.4l2.5-2.5"/>',
    # a magnifying glass
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    # a person in a circle
    "user": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="10" r="3.5"/>'
            '<path d="M5.5 19c1.5-3 4-4.5 6.5-4.5s5 1.5 6.5 4.5"/>',
}


def icon(name):
    paths = ICON_PATHS[name]
    return Markup(
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true">' + paths + "</svg>"
    )
