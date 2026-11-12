# detect-it

Detect whether a device is **mouse-only**, **touch-only**, or **hybrid**, and whether its **primary input** is a mouse or touch.

Modern devices blur the line between input methods. A laptop may have a trackpad and a touchscreen, a tablet may have a keyboard and mouse attached, and a phone may pair with a Bluetooth mouse. `detect-it` gives you a practical answer to two questions:

1. **What kinds of input does this device support?** Answer: `mouseOnly`, `touchOnly`, or `hybrid`.
2. **Which input should the interface optimize for?** Answer: `mouse` or `touch`.

Use it to choose hover-based or tap-based menus, size click targets, decide whether to show tooltips, or pick the right event model for your UI.

## Features

- **Three device categories:** `mouseOnly`, `touchOnly`, and `hybrid`.
- **Primary input detection:** reports `mouse` or `touch` based on the most likely way the user is interacting with the page.
- **Live updates:** optionally notifies you when the user switches input, for example when a touchscreen laptop's user starts using the trackpad or a tablet's keyboard is detached.
- **No dependencies:** a single file of plain JavaScript, under 2 KB minified and gzipped.
- **Safe in non-browser environments:** returns sensible defaults when `window` or `navigator` is unavailable, so server-side rendering doesn't break.
- **TypeScript types included.**

## Installation

Using npm:

```bash
npm install detect-it
```

Using yarn:

```bash
yarn add detect-it
```

Or load it directly in the browser:

```html
<script src="https://unpkg.com/detect-it/dist/detect-it.min.js"></script>
```

## Quick start

```js
import { detectIt } from 'detect-it';

const info = detectIt();

console.log(info.deviceType);   // 'mouseOnly' | 'touchOnly' | 'hybrid'
console.log(info.primaryInput); // 'mouse' | 'touch'

if (info.primaryInput === 'touch') {
  document.body.classList.add('use-large-targets');
} else {
  document.body.classList.add('use-hover-menus');
}
```

## API

### `detectIt()`

Returns a snapshot of the device's input capabilities at the moment it is called.

```ts
interface DetectItResult {
  deviceType: 'mouseOnly' | 'touchOnly' | 'hybrid';
  primaryInput: 'mouse' | 'touch';
  hasMouse: boolean;
  hasTouch: boolean;
  hasHover: boolean;     // true if the primary pointer can hover
  hasCoarsePointer: boolean; // true if the primary pointer is imprecise (for example, a finger)
}
```

### `onInputChange(callback)`

Registers a listener that runs whenever the detected primary input changes. It returns an unsubscribe function.

```js
import { onInputChange } from 'detect-it';

const unsubscribe = onInputChange((info) => {
  console.log('Primary input is now', info.primaryInput);
});

// Later, when you no longer need updates:
unsubscribe();
```

Listeners fire only when `primaryInput` changes, not on every input event, so they are safe to use for UI switching.

### `detectItOptions` (optional)

Some applications need to adjust the defaults. You can pass options to `detectIt()`:

```js
const info = detectIt({
  // Treat the device as touch-primary when it reports touch support,
  // even if a mouse was detected more recently.
  preferTouch: false,

  // Value to return when detection is impossible (for example, during SSR).
  fallback: { deviceType: 'mouseOnly', primaryInput: 'mouse' }
});
```

## How it works

`detect-it` combines several signals. No single browser API is reliable on its own, so the library weighs them together.

| Signal | Source | What it tells us |
|---|---|---|
| Touch support | `navigator.maxTouchPoints`, `'ontouchstart' in window` | The device can receive touch input |
| Hover capability | `matchMedia('(hover: hover)')` | The primary pointer can hover over elements |
| Pointer precision | `matchMedia('(pointer: coarse)')` | The primary pointer is a finger rather than a precise device |
| Recent input | `pointermove`, `pointerdown`, and `touchstart` events | Which input the user has used most recently |

The classification rules are:

- **`touchOnly`**: touch is supported, and no mouse or hover-capable pointer is detected.
- **`mouseOnly`**: no touch support is detected, or the device reports a fine pointer with hover and no touch.
- **`hybrid`**: both touch and a hover-capable mouse or trackpad are available.

For `primaryInput`, the library uses the most recent interaction once the user has interacted with the page. Before any interaction, it uses the media queries above. If the page has been open for a while without interaction, it falls back to `pointer: coarse` to decide between `touch` and `mouse`.

## Browser support

| Browser | Minimum version |
|---|---|
| Chrome | 79 |
| Edge | 79 |
| Firefox | 75 |
| Safari | 13.1 |
| iOS Safari | 13.4 |
| Android Chrome | 79 |

Older browsers still receive a result, but `hasHover` and `hasCoarsePointer` may be `false` because the media queries are unsupported. In that case the library classifies based on touch support alone.

## Limitations

Device input detection is inherently heuristic. Keep these caveats in mind:

- **Detection describes capability, not intent.** A device can have a touchscreen and a mouse connected, but the user may prefer one. Use `primaryInput` to pick a sensible default, and let users override it if your app allows.
- **Browsers can lie or simplify.** Some privacy-focused browsers report fewer touch points or hide hover support. The result is then conservative rather than wrong, but it may not match the hardware exactly.
- **Input can change at any time.** Plugging in a keyboard, pairing a Bluetooth mouse, or docking a tablet can change the result. Use `onInputChange` if your UI must respond.
- **Not a security or fingerprinting tool.** The output is intentionally coarse. Do not use it to identify individual users.

## Example: adapting a navigation menu

```js
import { detectIt, onInputChange } from 'detect-it';

const nav = document.querySelector('.nav');

function applyInputMode({ primaryInput }) {
  nav.dataset.inputMode = primaryInput;
}

applyInputMode(detectIt());
onInputChange(applyInputMode);
```

```css
/* Hover menus for mouse users */
.nav[data-input-mode="mouse"] .submenu {
  display: none;
}
.nav[data-input-mode="mouse"] .item:hover .submenu {
  display: block;
}

/* Larger tap targets for touch users */
.nav[data-input-mode="touch"] .item {
  min-height: 48px;
  padding: 12px 16px;
}
```

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/detect-it.git
cd detect-it
npm install
```

Common scripts:

```bash
npm test          # run the unit test suite
npm run build     # build the distributable files into dist/
npm run lint      # check code style
npm run typecheck # validate the TypeScript types
```

Tests run in a headless browser through the included test harness, so both browser-specific media query results and the server-side fallback are covered.

## Contributing

Contributions are welcome. Before opening a pull request:

1. Open an issue describing the change, especially if it affects the classification rules.
2. Add or update tests for any new detection signal or browser workaround.
3. Run `npm test` and `npm run lint`.
4. Describe the target devices and browsers you tested on in the pull request.

Bug reports are most helpful when they include the browser name and version, the device type, and the output of `detectIt()`.

## License

Released under the MIT License. See `LICENSE` for details.
