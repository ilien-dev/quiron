# scrollpath

A plugin for defining custom scroll paths.

scrollpath lets you describe how a page, container, or element should scroll: along a straight line, a curve, a sequence of waypoints, or a path you compute at runtime. Instead of relying only on the browser's default scrolling, you define a path once and drive scroll position along it with progress values, scroll events, or user input.

## Why scrollpath?

Native scrolling moves linearly along the y-axis (or x-axis) and offers little control over pacing, easing, or direction. Common needs like scrollytelling, parallax storytelling, guided tours, and animated page transitions usually end up as ad hoc scroll listeners that are hard to maintain. scrollpath gives these behaviors a declarative shape:

- **Paths are data.** A path is a list of points, a parametric function, or a combination of both. You can serialize, share, and test it.
- **Progress is normalized.** Every path maps a value from `0` to `1` onto a position along its length, so the same animation logic works regardless of the path's geometry.
- **Scrolling stays native.** scrollpath updates the real scroll position of the target, so accessibility features, keyboard navigation, and screen readers keep working.
- **It is framework-agnostic.** The core has no dependencies. Thin adapters are available for common frameworks.

## Features

- Linear, polyline, cubic Bézier, and custom parametric paths
- Arc-length parameterization, so progress is evenly spaced along the path
- Easing functions applied to progress
- Multiple targets: window, any scrollable element, or a set of elements
- Snap points and anchors at defined positions along the path
- Event hooks for enter, exit, and progress changes
- Reduced-motion support that respects `prefers-reduced-motion`
- TypeScript types included

## Installation

Using npm:

```bash
npm install scrollpath
```

Using pnpm or yarn:

```bash
pnpm add scrollpath
# or
yarn add scrollpath
```

From a CDN, for quick prototyping:

```html
<script type="module">
  import { createScrollPath } from "https://cdn.example.com/scrollpath/latest/scrollpath.esm.js";
</script>
```

Replace the CDN URL with the one you use for your project.

## Quick start

The smallest working example scrolls the window along a diagonal path while the user scrolls down the page:

```js
import { createScrollPath, linear } from "scrollpath";

const path = createScrollPath({
  target: window,
  points: [
    { x: 0, y: 0 },
    { x: 200, y: 1200 },
  ],
  easing: linear,
});

path.attach();
```

Once attached, scrollpath listens to the target's scroll events and maps the current scroll progress onto the path. Each point on the path is translated into a scroll position for the target.

To drive the path manually, for example from a slider or a timeline:

```js
path.seek(0.5); // move to the halfway point along the path
```

## Defining paths

### Polyline

A polyline connects points in order:

```js
import { polyline } from "scrollpath";

const route = polyline([
  { x: 0, y: 0 },
  { x: 0, y: 800 },
  { x: 400, y: 800 },
  { x: 400, y: 1600 },
]);
```

### Cubic Bézier

Use a cubic Bézier when you want a smooth curve:

```js
import { bezier } from "scrollpath";

const curve = bezier({
  start: { x: 0, y: 0 },
  control1: { x: 100, y: 400 },
  control2: { x: -100, y: 800 },
  end: { x: 0, y: 1200 },
});
```

### Parametric functions

For paths that depend on math or runtime data, supply a function that takes `t` in the range `[0, 1]` and returns a point:

```js
import { parametric } from "scrollpath";

const spiral = parametric((t) => {
  const angle = t * Math.PI * 4;
  const radius = 300 * t;
  return {
    x: Math.cos(angle) * radius,
    y: t * 3000 + Math.sin(angle) * radius,
  };
});
```

### Combining paths

Paths can be concatenated into a single timeline. Each segment receives an equal share of progress unless you set `weight`:

```js
import { sequence } from "scrollpath";

const journey = sequence([
  { path: route, weight: 2 },
  { path: curve, weight: 1 },
]);
```

## Targets

By default, scrollpath uses `window`. You can point it at any scrollable element:

```js
const path = createScrollPath({
  target: document.querySelector("#gallery"),
  points: [{ x: 0, y: 0 }, { x: 0, y: 2000 }],
});
```

To control several elements with one path, pass an array. Each element receives the same normalized progress:

```js
const path = createScrollPath({
  target: [...document.querySelectorAll(".panel")],
  points: [{ x: 0, y: 0 }, { x: 0, y: 1000 }],
});
```

## Easing

Easing functions transform progress before it is applied to the path. Built-in options include `linear`, `easeIn`, `easeOut`, `easeInOut`, and `steps(n)`. You can also pass your own function:

```js
import { createScrollPath } from "scrollpath";

const path = createScrollPath({
  target: window,
  points: [{ x: 0, y: 0 }, { x: 0, y: 2000 }],
  easing: (p) => p * p, // quadratic ease-in
});
```

## Anchors and snapping

Anchors mark named positions along a path. You can jump to them or snap to the nearest one after the user stops scrolling:

```js
const path = createScrollPath({
  target: window,
  points: [{ x: 0, y: 0 }, { x: 0, y: 3000 }],
  anchors: {
    intro: 0,
    features: 0.4,
    pricing: 0.75,
  },
  snap: { anchors: true, delay: 150 },
});

path.goTo("features");
```

`delay` is the time in milliseconds to wait after scrolling stops before snapping.

## Events

Subscribe to changes in progress or to boundaries crossed:

```js
path.on("progress", ({ value }) => {
  console.log("Progress:", value.toFixed(2));
});

path.on("enter", () => console.log("Path started"));
path.on("exit", () => console.log("Path finished"));
path.on("anchor", ({ name }) => console.log("Reached", name));
```

To remove a listener, call `path.off(eventName, handler)`.

## Reduced motion

scrollpath checks `prefers-reduced-motion` on attach. When the preference is set, it disables snapping and easing and applies progress changes immediately. You can override this behavior:

```js
const path = createScrollPath({
  target: window,
  points: [{ x: 0, y: 0 }, { x: 0, y: 2000 }],
  respectReducedMotion: false,
});
```

Only disable this option when you have a specific reason and have tested the experience with motion sensitivity in mind.

## API reference

### `createScrollPath(options)`

Creates a scroll path controller.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `target` | `Window \| Element \| Element[]` | `window` | What to scroll. |
| `points` | `Point[]` | required | Points defining the path. |
| `easing` | `(p: number) => number` | `linear` | Easing applied to progress. |
| `anchors` | `Record<string, number>` | `{}` | Named progress positions. |
| `snap` | `{ anchors?: boolean; delay?: number }` | `false` | Snapping behavior. |
| `respectReducedMotion` | `boolean` | `true` | Honor the reduced-motion preference. |

### Controller methods

| Method | Description |
| --- | --- |
| `attach()` | Start listening to scroll and resize events. |
| `detach()` | Stop listening and release listeners. |
| `seek(progress)` | Move to a progress value between `0` and `1`. |
| `goTo(anchorName)` | Move to a named anchor. |
| `getProgress()` | Return the current progress value. |
| `on(event, handler)` | Subscribe to an event. |
| `off(event, handler)` | Unsubscribe from an event. |
| `destroy()` | Detach and clear all listeners and state. |

## Browser support

scrollpath supports current versions of Chrome, Firefox, Safari, and Edge. It relies on `IntersectionObserver` and `requestAnimationFrame`. For older browsers, include the appropriate polyfills.

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/scrollpath.git
cd scrollpath
npm install
```

Common scripts:

```bash
npm run build    # produce ESM and CJS bundles in dist/
npm test         # run unit tests
npm run dev      # start the example playground
npm run lint     # run the linter
```

Before opening a pull request, run the full test suite and add tests for any new path type or option.

## Contributing

Issues and pull requests are welcome. For larger changes, open an issue first to discuss the design. Keep changes focused, follow the existing code style, and include documentation updates alongside code changes.

## License

Released under the MIT License. See `LICENSE` for details.

---

I wrote this without opening the project, so the API names, option defaults, install commands, CDN URL, and repository link are plausible placeholders rather than facts about your code. Before publishing, check them against the actual exports and update the examples. I can also write the file to the project root and reconcile it with the source if you point me to the entry point or share the main module.
