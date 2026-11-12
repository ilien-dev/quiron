Default scroll bars are the last unstyled corner of many otherwise polished interfaces. You can spend hours on typography, spacing, and a dark mode, and then a chunky gray bar appears on the right edge and spoils it.

Fixing this takes far less code than most people expect. In this post we'll build a themed, rounded scroll bar with a hover state, and it works in Chrome, Edge, Safari, and Firefox. The whole thing is 24 lines of CSS.

## The finished code

Here is the complete snippet. We'll go through it piece by piece afterward.

```css
:root {
  --track: #1e1e2e;
  --thumb: #7c3aed;
  --hover: #a78bfa;
}

@supports not selector(::-webkit-scrollbar) {
  * {
    scrollbar-width: thin;
    scrollbar-color: var(--thumb) var(--track);
  }
}

::-webkit-scrollbar {
  width: 12px;
  height: 12px;
  background: var(--track);
}

::-webkit-scrollbar-thumb {
  background: var(--thumb);
  border: 3px solid var(--track);
  border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--hover);
}
```

Not counting blank lines, that is exactly 24. Let's see what each part does.

## Step 1: Put your colors in variables

```css
:root {
  --track: #1e1e2e;
  --thumb: #7c3aed;
  --hover: #a78bfa;
}
```

A scroll bar has two visible parts. The **track** is the channel it sits in, and the **thumb** is the draggable handle. We also want a lighter thumb color for hover.

Custom properties keep these three values in one place. If you later add a light theme, you can override them under a `[data-theme="light"]` selector and the scroll bar follows automatically.

## Step 2: Style the WebKit scroll bar

Chrome, Edge, Opera, and Safari all understand the `::-webkit-scrollbar` family of pseudo-elements. The three we need are:

- `::-webkit-scrollbar` is the scroll bar as a whole
- `::-webkit-scrollbar-thumb` is the draggable handle
- `::-webkit-scrollbar-thumb:hover` is the handle while the pointer is over it

```css
::-webkit-scrollbar {
  width: 12px;
  height: 12px;
  background: var(--track);
}
```

`width` controls vertical scroll bars and `height` controls horizontal ones. Setting both means your code blocks and wide tables get the same treatment as the page itself. The `background` on this element paints the track, so we don't need a separate `::-webkit-scrollbar-track` rule. That saves three lines.

## Step 3: Make the thumb look intentional

```css
::-webkit-scrollbar-thumb {
  background: var(--thumb);
  border: 3px solid var(--track);
  border-radius: 999px;
}
```

This is where the polish comes from. The `border-radius` gives us a pill shape. The border is the interesting part. It's drawn in the same color as the track, so it looks like padding around the thumb. The thumb appears to float inside the channel instead of touching its edges. With a 12px bar and a 3px border, you get a slim 6px handle that is still easy to grab.

The hover rule is a single color change:

```css
::-webkit-scrollbar-thumb:hover {
  background: var(--hover);
}
```

Small feedback like this tells users the element is interactive.

## Step 4: Cover Firefox

Firefox doesn't support the WebKit pseudo-elements. It uses two standard properties instead:

- `scrollbar-width` accepts `auto`, `thin`, or `none`
- `scrollbar-color` takes the thumb color first, then the track color

Chrome has supported these standard properties since version 121. That introduces a trap. **If you set `scrollbar-color` or `scrollbar-width` on an element in Chrome, it ignores your `::-webkit-` rules for that element.** Your rounded thumb and hover color would silently disappear.

The fix is a feature query:

```css
@supports not selector(::-webkit-scrollbar) {
  * {
    scrollbar-width: thin;
    scrollbar-color: var(--thumb) var(--track);
  }
}
```

This block only applies in browsers that *don't* recognize the WebKit selector, which in practice means Firefox. Chromium browsers and Safari skip it and use the detailed styles above. Each browser gets the best option it supports, and neither set of rules interferes with the other.

You lose a few things in Firefox: there are no rounded corners, no inset border, and no hover color. You still get a themed, slim bar that matches your design, and that's a reasonable trade for a short stylesheet.

## Things to know before shipping

**Scope it if you need to.** The snippet styles every scroll bar on the page. To limit it to one container, replace the selectors with something like `.panel::-webkit-scrollbar` and change `*` to `.panel`.

**Don't hide scroll bars.** `scrollbar-width: none` is tempting, but it removes a visual cue that content continues below the fold. Style the bar instead of removing it.

**Mind contrast.** Your thumb should stand out from the track clearly enough for users with low vision. A quick check with any contrast tool is worth the minute it takes. Aim for at least 3:1 between thumb and track.

**Remember touch devices.** Mobile browsers and macOS with overlay scroll bars often ignore or override custom styling. That's fine. Treat the custom bar as an enhancement rather than a requirement.

**Keep the width usable.** Going much below 8px makes the handle hard to grab with a mouse. Twelve pixels with a 3px border is a comfortable middle ground.

## Wrapping up

With 24 lines you get a themeable, rounded scroll bar with hover feedback and a graceful fallback in Firefox. The main ideas to remember are:

1. Use CSS variables so the colors live in one place.
2. Style the thumb with a track-colored border to create the floating effect.
3. Wrap the standard properties in `@supports not selector(::-webkit-scrollbar)` so they don't cancel your WebKit styles in Chrome.

Copy the snippet, swap in your brand colors, and see how it feels on your own site. If you've found a neat variation, such as gradients on the thumb or an animated width on hover, share it in the comments.
