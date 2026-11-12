# blueprint3d

Build interior spaces in 3D.

blueprint3d is a JavaScript library for designing rooms and furnishing them in the browser. Draw a floor plan in 2D, switch to a 3D view, and drop in furniture, doors, and windows.

## Features

- **2D floor planner**: draw, move, and delete walls on a grid, with automatic room detection and live dimensions.
- **3D view**: orbit, pan, and zoom around a rendered model of your plan.
- **Item placement**: add floor, wall, and in-wall items such as doors and windows, which snap to valid surfaces.
- **Textures**: apply materials to walls and floors individually.
- **Save and load**: serialize a whole design to JSON and restore it later.

## Getting started

You will need Node.js and npm.

```bash
git clone <repository-url>
cd blueprint3d
npm install
npm run build
```

The build writes the bundled library to `dist/`. To try the example application, serve the `example/` directory with any static file server:

```bash
npx http-server example
```

Then open the printed address in a browser.

## Usage

Include the bundled script and create an instance pointed at the DOM elements you want to use:

```js
const blueprint3d = new BP3D.Blueprint3d({
  floorplannerElement: 'floorplanner-canvas',
  threeElement: '#viewer',
  textureDir: 'models/textures/',
  widget: false
});

// Load a saved design
blueprint3d.model.loadSerialized(savedJson);

// Add an item to the scene
blueprint3d.model.scene.addItem(itemType, modelUrl, metadata);

// Export the current design
const json = blueprint3d.model.exportSerialized();
```

## Project structure

| Directory | Contents |
| --- | --- |
| `src/core` | Shared utilities, configuration, and dimensioning |
| `src/model` | Data model: floor plan, walls, corners, rooms, scene |
| `src/floorplanner` | 2D editor and canvas rendering |
| `src/three` | 3D rendering, camera controls, lighting |
| `src/items` | Item types and their placement rules |
| `example` | A complete demo application |

The model layer is independent of both views. The 2D floor planner and the 3D renderer each observe the same model, so a change in one appears in the other.

## Browser support

blueprint3d needs a browser with WebGL enabled. Current versions of Chrome, Firefox, Edge, and Safari all work.

## Contributing

Contributions are welcome.

1. Fork the repository and create a branch for your change.
2. Keep pull requests focused on one fix or feature.
3. Describe what changed and why, with screenshots for visual changes.
4. Open an issue first if you are planning something large.

Bug reports are most useful when they include the browser version, steps to reproduce, and the serialized design if you can share it.

## License

Released under the MIT License. See `LICENSE` for the full text.
