# Creating a Custom Scroll Bar in 24 Lines of CSS

Default browser scrollbars are functional but rarely match the aesthetic of a polished website. The good news is that styling scrollbars has become much easier than it used to be, and you can build something that looks intentional with a surprisingly small amount of CSS. Let's walk through how to do it.

## The WebKit Approach

Most Chromium-based browsers, along with Safari, support a set of pseudo-elements prefixed with `-webkit-scrollbar` that give you fine-grained control over every part of the scrollbar. Here's a complete example:

```css
::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

Let's break this down piece by piece.

`::-webkit-scrollbar` targets the entire scrollbar element itself, and this is where you set its overall width. For a vertical scrollbar, this property controls how wide the bar appears. If you were styling a horizontal scrollbar, this same property would control its height instead.

`::-webkit-scrollbar-track` styles the background track that the thumb slides along. Giving it a border radius and a light background color helps it blend into the page rather than looking like a jarring gray strip along the edge.

`::-webkit-scrollbar-thumb` is the draggable part, the piece users actually grab and move. This is usually where you want your primary styling to live, since it's the most visually prominent part of the scrollbar.

The `:hover` pseudo-class on the thumb adds a nice bit of interactivity, darkening the thumb slightly when a user hovers over it, giving subtle feedback that the element is interactive.

## Rounding Out the Corners

If your scrollbar track and thumb meet at a corner, like when both vertical and horizontal scrollbars are present, you can style that corner too:

```css
::-webkit-scrollbar-corner {
  background: transparent;
}
```

Setting it to transparent usually looks cleaner than leaving the default gray square.

## Don't Forget Firefox

Firefox doesn't support the `-webkit-scrollbar` pseudo-elements, but it does support a simpler set of standardized properties:

```css
* {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}
```

`scrollbar-width` accepts `auto`, `thin`, or `none`, giving you coarse control over the scrollbar's size. `scrollbar-color` takes two values: the thumb color first, then the track color. It's much less granular than the WebKit approach, but it ensures your scrollbar doesn't look completely out of place for Firefox users.

## Putting It All Together

Combining both approaches gives you consistent styling across the vast majority of browsers your users will actually be running:

```css
* {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}

::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

## A Few Things to Keep in Mind

Custom scrollbars are purely cosmetic, so make sure you're not sacrificing usability for aesthetics. Keep the thumb wide enough to comfortably grab with a mouse, and avoid making the contrast between the thumb and track so low that users with low vision struggle to see it. It's also worth testing on an actual trackpad and touchscreen, since scrollbar behavior can vary across input methods, and some mobile browsers hide scrollbars by default regardless of what CSS you write.

## Wrapping Up

With just a handful of CSS rules, you can take a scrollbar from a default, forgettable UI element to something that feels like a deliberate part of your design. It won't work identically everywhere, browser support for scrollbar styling is still inconsistent, but with the WebKit pseudo-elements and Firefox's standardized properties combined, you'll get solid coverage across the browsers most of your users are running.
