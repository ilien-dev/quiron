# termbox

Library for writing text-based user interfaces.

termbox provides a small foundation for building interactive applications that run inside a terminal. It lets you work with a grid of character cells, control their appearance, and respond to keyboard and mouse input without scattering terminal escape sequences throughout your application.

Use it to build command-line tools with interactive screens, dashboards, editors, file browsers, menus, and other applications where plain text output is not enough.

## Overview

A terminal interface has two basic jobs: display information and react to input. termbox keeps those jobs explicit. Your application decides what belongs on the screen, updates the appropriate cells, and presents the result. Incoming events tell your application when the user presses a key, interacts with the mouse, or changes the terminal size.

This approach gives you control over layout and behavior while keeping the underlying interface compact. You can start with a single screen and introduce your own components as the application grows.

termbox is a rendering and input foundation. Application structure, widget behavior, navigation, and data management remain yours to define.

## Core concepts

### The screen is a grid

Think of the terminal as a rectangular collection of cells. Each cell contains a character and appearance information, such as foreground and background colors.

Your application draws by choosing coordinates and updating cells. A label occupies several adjacent cells; a panel combines text, borders, and background colors. Larger interfaces use the same building blocks.

### Drawing and presentation are separate

Prepare the screen contents before presenting them. Keeping these operations separate makes it easier to render a complete frame consistently and avoid exposing intermediate layout changes.

A typical redraw clears or updates the drawing surface, renders the visible interface, positions the cursor when needed, and presents the completed result.

### Input arrives as events

Interactive programs respond to events rather than repeatedly reading lines of text. Handle each event according to the current application state, then redraw when that state changes.

Keep input handling separate from rendering where practical. This makes shortcuts, navigation, and editing behavior easier to understand and maintain.

## Getting started

Begin with the build and installation instructions supplied with the version of termbox you are using. Platform support, dependencies, build options, and integration details can vary between distributions and language bindings.

Once the library is available to your project:

1. Initialize termbox and check whether initialization succeeded.
2. Read the terminal dimensions.
3. Draw a simple message.
4. Present the screen.
5. Wait for an input event.
6. Exit on a designated key.
7. Shut down termbox and restore the terminal.

Start small. A screen displaying a message and an exit shortcut is enough to verify that initialization, rendering, input, and cleanup work correctly.

## Application structure

The following pseudocode illustrates a basic event loop. It describes the workflow rather than a specific language binding or API:

```text
initialize terminal
try:
    running = true

    while running:
        read current dimensions
        draw application state
        present screen

        event = wait for event

        if event requests exit:
            running = false
        else:
            update application state from event
finally:
    restore terminal
```

For applications with background activity, arrange for updates to reach the event loop without allowing concurrent code to modify the same screen state unpredictably.

## Layout and resizing

Terminal dimensions can change while your application is running. Recalculate layouts after resize events and avoid assuming that the initial width and height remain valid.

Define how each screen behaves when space is limited. You might hide secondary panels, shorten labels, enable scrolling, or display a compact message explaining the minimum usable size.

Check coordinates before drawing. Layout calculations should handle narrow windows, short windows, and empty content without producing invalid positions.

## Text, color, and input

Text storage length and visible terminal width are different concepts. Some characters occupy multiple cells, and combining characters can complicate cursor placement. Test the languages and symbols your application intends to display.

Use color to support meaning, with text or symbols providing additional cues. A selected item should remain recognizable when a color scheme changes or contrast is limited.

Choose consistent keyboard shortcuts and make essential actions discoverable. Terminal environments can differ in how they report certain keys and combinations, so test important interactions in the environments you support.

## Cleanup and error handling

Always restore the terminal when your application exits, including when an operation fails. Without reliable cleanup, users may return to a shell with unexpected input or display settings.

Check initialization results before drawing or reading events. Keep error reporting understandable, and arrange cleanup so that it runs once.

During development, consider writing diagnostic output to a file. Printing logs directly into an active interface can disrupt the screen and make problems harder to inspect.

## Testing

Test rendering and interaction at several terminal sizes. Include empty lists, long labels, rapid input, repeated resizing, and application shutdown.

Where possible, keep application state and layout calculations independent of terminal access. These parts can be tested without an interactive terminal session.

Manual testing still matters: verify cursor behavior, text alignment, colors, and terminal restoration in supported environments.

## Contributing

Contributions are welcome. Explain the problem your change addresses, keep changes focused, and include relevant reproduction steps or validation results.

Before submitting, check the repository’s contribution guidelines and existing discussions.

## License

See the license included with your distribution for the terms governing use, modification, and redistribution.
