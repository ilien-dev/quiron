# Want CSS variables in media query declarations? Try this!

If you've ever tried to use a CSS custom property (a CSS variable) inside a media query, you've probably hit a frustrating wall. Something like this just doesn't work:

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

Open your dev tools and you will see the media query just gets ignored. There are no errors and no warnings. It just fails. So why doesn't it work, and how do we get variables into our media queries?

## Why doesn't this work?

CSS custom properties are resolved at *render time*, based on the cascade. They depend on the DOM, inheritance and specificity. Media queries are evaluated by the browser *before* any of that cascade logic happens. The browser needs the layout information before it renders the page, so it can't wait for a custom property to be resolved.

In short, custom properties are a run-time concept, and media queries are evaluated at an earlier stage. The two are not compatible by design, at least not natively.

## The workaround: preprocessing

CSS custom properties don't work here, so the most common approach I've seen is to use build-time variables from a preprocessor like Sass or Less, or from a PostCSS plugin.

Here's an example using Sass:

```scss
$breakpoint-tablet: 768px;

@media (min-width: $breakpoint-tablet) {
  .container {
    flex-direction: row;
  }
}
```

Sass variables are resolved during compilation, before the CSS ever reaches the browser, so this works. The `$breakpoint-tablet` variable gets replaced with `768px` in the final compiled CSS, and the media query works.

If you're not using Sass, PostCSS has plugins like `postcss-custom-media` that let you define media query values you can use again and again:

```css
@custom-media --tablet (min-width: 768px);

@media (--tablet) {
  .container {
    flex-direction: row;
  }
}
```

This is based on a CSS spec proposal (Media Queries Level 5). I like it as a preview of where native CSS might eventually go, even though browser support isn't there yet.

## Keeping things in sync

One problem with this approach is keeping your breakpoints in sync. You have CSS custom properties for runtime styling and Sass or PostCSS variables for media queries, and it's easy for those two sources of truth to drift apart if you are not careful.

A common pattern is to define your breakpoints once, in a central configuration file. That might be a Sass `_variables.scss` partial or a PostCSS custom media file. Then a build step generates your runtime CSS custom properties from that same source. Some teams use JavaScript-based design tokens as the source of truth and export them into both formats automatically.

## Using JavaScript as a bridge

If you want your media queries to be dynamic and controlled by something like a theme switcher, you can also use JavaScript and update styles with `matchMedia`:

```js
const tabletQuery = window.matchMedia('(min-width: 768px)');

function handleTabletChange(e) {
  document.documentElement.classList.toggle('is-tablet', e.matches);
}

tabletQuery.addEventListener('change', handleTabletChange);
handleTabletChange(tabletQuery);
```

This moves the responsibility out of CSS and into JavaScript and gives you full control there. That's useful when your breakpoints need to change at runtime, for example when your breakpoints are driven by user settings.

## Wrapping up

I love CSS custom properties for a lot of things. Media queries just aren't one of those things, at least not yet. Until browser support catches up with proposals like custom media queries, your best bet is to use your preprocessor or build tool to keep things DRY.

What I'd take from all this: keep your *build-time* breakpoint values (Sass, PostCSS) separate from your *run-time* custom properties, and find a single source of truth to keep them in sync. It's a bit of extra setup, but it saves you a lot of confusion down the road.
