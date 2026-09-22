# Want CSS variables in media query declarations? Try this!

If you've ever tried to use a CSS custom property (a CSS variable) inside a media query, you've probably run into a frustrating wall. Something like this just doesn't work:

```css
:root {
  --breakpoint-tablet: 768px;
}

@media (min-width: var(--breakpoint-tablet)) {
  .container {
    flex-direction: row;
  }
}
```

Open your dev tools, and you'll see the media query simply gets ignored. No errors, no warnings — it just silently fails. So what's going on, and how do we actually get variable-like behavior in our media queries?

## Why Doesn't This Work?

CSS custom properties are resolved at *render time*, based on the cascade — they depend on the DOM, inheritance, and specificity. Media queries, on the other hand, are evaluated by the browser *before* any of that cascade logic kicks in. The browser needs to know the layout rules before it even renders the page, so it can't wait around for a custom property to resolve.

In short: custom properties are a run-time concept, and media queries are evaluated at a different, earlier stage. They're just not compatible by design, at least not natively.

## The Workaround: Preprocessing

Since native CSS variables won't cut it here, the most common approach is to fall back on build-time variables using a preprocessor like Sass or Less, or a PostCSS plugin.

Here's an example using Sass:

```scss
$breakpoint-tablet: 768px;

@media (min-width: $breakpoint-tablet) {
  .container {
    flex-direction: row;
  }
}
```

Since Sass variables are resolved at compile time — before the CSS ever reaches the browser — this works perfectly. The `$breakpoint-tablet` variable gets swapped out for `768px` in the final compiled CSS, and the media query works exactly as expected.

If you're not using Sass, PostCSS has plugins like `postcss-custom-media` that let you define reusable media query values:

```css
@custom-media --tablet (min-width: 768px);

@media (--tablet) {
  .container {
    flex-direction: row;
  }
}
```

This is actually based on a CSS spec proposal (Media Queries Level 5), so it's a nice preview of where native CSS might eventually go, even though browser support isn't there yet.

## Keeping Things In Sync

One challenge with this approach is keeping your breakpoints in sync between your CSS custom properties (used for runtime styling) and your preprocessor/PostCSS variables (used for media queries). It's easy for these two sources of truth to drift apart if you're not careful.

A common pattern is to define your breakpoints once, in a central config file — whether that's a Sass `_variables.scss` partial or a PostCSS custom media file — and then generate your runtime CSS custom properties from that same source using a build step. Some teams use JavaScript-based design tokens as the true source, exporting them into both formats automatically.

## Using JavaScript As A Bridge

If you want your media queries to be dynamic and controlled by something like a theme switcher, you can also lean on JavaScript to update styles based on `matchMedia`:

```js
const tabletQuery = window.matchMedia('(min-width: 768px)');

function handleTabletChange(e) {
  document.documentElement.classList.toggle('is-tablet', e.matches);
}

tabletQuery.addEventListener('change', handleTabletChange);
handleTabletChange(tabletQuery);
```

This approach shifts the responsibility away from CSS entirely and gives you full control in JS, which can be useful if your breakpoints need to be dynamic (for example, driven by user settings) rather than static.

## Wrapping Up

CSS custom properties are fantastic for a lot of use cases, but media queries just aren't one of them — at least not yet. Until browser support catches up with proposals like custom media queries, your best bet is to lean on your preprocessor or build tool to keep things DRY.

The key takeaway: separate your *build-time* breakpoint values (Sass, PostCSS) from your *run-time* custom properties, and find a single source of truth to keep them in sync. It's a bit of extra setup, but it saves you from a lot of confusion down the road.
