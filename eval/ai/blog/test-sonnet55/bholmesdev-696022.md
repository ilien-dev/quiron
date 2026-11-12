# Want CSS variables in media query declarations? Try this!

You define your breakpoints once as custom properties, feel good about it, and write this:

```css
:root {
  --bp-md: 768px;
}

@media (min-width: var(--bp-md)) {
  .sidebar { display: block; }
}
```

Nothing happens. No error, and the rule never applies. This trips up a lot of people, so let's look at why it fails and what to do instead.

## Why it doesn't work

Custom properties are resolved per element, through the cascade and inheritance. `var(--bp-md)` only means something when the browser is computing styles for a specific node.

A media query isn't attached to any element. The browser evaluates it against the viewport or device before it matches rules to elements. At that point there is no element, no cascade, and no `:root` to read from, so `var()` has nothing to resolve against. The declaration is invalid and the whole at-rule is dropped.

Container queries have the same limitation: `var()` isn't allowed inside the condition.

## Option 1: Resolve it at build time

The most practical fix is to move the variable out of the browser and into your build step. If you use Sass:

```scss
$bp-md: 768px;

@media (min-width: $bp-md) {
  .sidebar { display: block; }
}
```

Sass variables are replaced during compilation, so the browser only ever sees `@media (min-width: 768px)`. The tradeoff is that the value is fixed at build time. You can't change it at runtime or per theme.

## Option 2: `@custom-media` with PostCSS

The Media Queries Level 5 draft includes `@custom-media`, which lets you name a whole query:

```css
@custom-media --md (min-width: 768px);

@media (--md) {
  .sidebar { display: block; }
}
```

This reads like CSS, not like a preprocessor. The [`postcss-custom-media`](https://github.com/csstools/postcss-plugins) plugin expands it at build time into plain media queries. Native browser support has been slow to arrive, so check current compatibility tables before shipping it without a build step.

You can keep your breakpoints in one shared file and import it everywhere:

```css
/* breakpoints.css */
@custom-media --sm (min-width: 480px);
@custom-media --md (min-width: 768px);
@custom-media --lg (min-width: 1200px);
```

## Option 3: Skip the query and let the value adapt

Often you don't need a media query at all. If the goal is "make this value bigger on bigger screens", a custom property combined with `clamp()` or `min()`/`max()` does it fluidly:

```css
:root {
  --gap: clamp(1rem, 2vw + 0.5rem, 3rem);
}

.grid {
  display: grid;
  gap: var(--gap);
}
```

There are no breakpoints to maintain, and the layout adjusts smoothly. This is a good fit for spacing, type sizes and padding. It's a poor fit for structural changes such as swapping a nav for a hamburger menu.

## Option 4: Override variables inside the query

This is the reverse of what you originally wanted, and it works natively. Keep the query values literal, but use the media query to change the variables:

```css
:root {
  --columns: 1;
  --pad: 1rem;
}

@media (min-width: 768px) {
  :root {
    --columns: 2;
    --pad: 2rem;
  }
}

@media (min-width: 1200px) {
  :root {
    --columns: 4;
  }
}

.grid {
  grid-template-columns: repeat(var(--columns), 1fr);
  padding: var(--pad);
}
```

The breakpoints are written in a few places, but all your components consume the variables and never think about viewport width. This keeps the media queries in one spot and the rest of the stylesheet clean.

## Option 5: Read the variable in JavaScript

If you really need the breakpoint to live in a CSS variable and drive behavior, read it at runtime:

```js
const bp = getComputedStyle(document.documentElement)
  .getPropertyValue('--bp-md')
  .trim();

const mql = window.matchMedia(`(min-width: ${bp})`);
mql.addEventListener('change', e => {
  document.body.classList.toggle('is-wide', e.matches);
});
```

Then style against `.is-wide` in your CSS. This works, but it adds JavaScript to something CSS should handle, and styles can flash before the script runs. Use it only when the value must come from the CSS side.

## Which one should you use?

- **Existing Sass setup:** use Sass variables.
- **Plain CSS with a PostCSS pipeline:** use `@custom-media`.
- **Fluid sizing:** use `clamp()` and skip the query.
- **Many components reacting to the same breakpoints:** override variables inside a few media queries.
- **Runtime-defined breakpoints:** use `matchMedia`, and accept the cost.

`var()` in a media query would be convenient, but the way the cascade works means it probably won't arrive in that form. Fortunately, the alternatives above cover almost every real use case.

Have you found another workaround? Share it in the comments.
