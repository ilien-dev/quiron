<invoke name="Write">
<parameter name="file_path">C:\Users\jesus\AppData\Local\Temp\quiron-gen-ntzben8s\README.md</parameter>
<parameter name="content"># layerJS

**layerJS: Javascript UI composition framework**

layerJS lets you build rich, app-like user interfaces from plain HTML. Instead of wiring up sliders, menus, overlays, and page transitions by hand, you describe your interface as a set of nested *stages*, *layers*, and *frames*, and layerJS takes care of positioning, scaling, scrolling, and animating between them.

It works with any backend, any CSS, and any other JavaScript library. There is no build step required and no templating language to learn.

## Why layerJS?

Modern interfaces are rarely a single scrolling page. They combine carousels, slide-in navigation, modal dialogs, parallax sections, and multi-step flows. Each of these patterns usually brings its own plugin, its own markup conventions, and its own quirks. layerJS replaces that patchwork with one consistent model:

- **Composable** – nest stages inside frames to build complex layouts out of simple pieces.
- **Declarative** – configure behavior with HTML attributes rather than imperative code.
- **Linkable** – every UI state maps to a URL, so deep links, the back button, and bookmarks just work.
- **Responsive** – frames can fit, fill, or scroll within their stage, adapting to any screen size.
- **Lightweight** – drop in a single script and start building.

## Core Concepts

| Concept   | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| **Stage** | A viewport: a rectangular area of the screen that displays content.         |
| **Layer** | A plane inside a stage. Multiple layers can be stacked on top of each other.|
| **Frame** | A piece of content inside a layer. A layer shows one active frame at a time.|

Switching which frame is visible in a layer is called a *transition*. Transitions can slide, fade, zoom, or use custom effects, and they can be triggered by links, gestures, or the JavaScript API.

## Installation

Via npm:

```bash
npm install layerjs
```

Or include it directly in your page:

```html
<link rel="stylesheet" href="layerjs.css">
<script src="layerjs.js"></script>
```

## Quick Start

```html
<div lj-type="stage" id="main">
  <div lj-type="layer" id="content" lj-default-frame="home">
    <div lj-type="frame" id="home">
      <h1>Welcome</h1>
      <a href="#about">About us</a>
    </div>
    <div lj-type="frame" id="about">
      <h1>About</h1>
      <a href="#home" lj-transition="right">Back</a>
    </div>
  </div>
</div>
```

Clicking **About us** transitions the layer to the `about` frame. The URL updates automatically, and the browser's back button returns you to `home`.

## JavaScript API

Everything you can do with markup is also available programmatically:

```js
const layer = layerJS.select('#content');

layer.transitionTo('about', { type: 'fade', duration: '400ms' });

layer.on('transitionFinished', (frameName) => {
  console.log(`Now showing: ${frameName}`);
});
```

## Frame Fitting

Control how a frame sizes itself within its stage using `lj-fit-to`:

- `width` – scale to the stage width and scroll vertically
- `height` – scale to the stage height and scroll horizontally
- `contain` – fit entirely within the stage
- `cover` – fill the stage, cropping if necessary
- `fixed` – keep the original size

## Browser Support

layerJS supports all current evergreen browsers, including Chrome, Firefox, Safari, and Edge, on both desktop and mobile.

## Contributing

Bug reports, feature ideas, and pull requests are welcome. Please open an issue to discuss significant changes before submitting a PR, and make sure the test suite passes with `npm test`.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
</parameter>
</invoke>
