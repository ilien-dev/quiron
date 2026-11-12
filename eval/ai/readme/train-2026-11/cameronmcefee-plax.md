# plax

**JQuery powered parallaxing**

plax is a jQuery plugin that brings depth and movement to layered illustrations. It shifts elements in response to the position of the pointer, allowing foreground and background layers to move at different speeds. The result is a parallax effect that makes a flat composition feel more dimensional.

Use plax to add a little life to a homepage illustration, product scene, title graphic, or decorative background. Start with a few positioned elements, give each one a movement range, and let plax coordinate their motion.

## How it works

A parallax scene consists of layers arranged within a shared container. Each layer has a starting position and a permitted horizontal and vertical movement range.

As the pointer moves, plax offsets those layers. Elements with larger ranges appear to move more prominently; elements with smaller ranges seem farther away. Mixing the ranges creates an impression of depth without requiring a 3D renderer.

The artwork does most of the storytelling. plax supplies the motion.

## Requirements

You will need:

- jQuery, loaded before plax.
- The plax JavaScript file.
- A container with positioned elements.
- Artwork or HTML elements that have room to move.

The examples below assume the plugin is available as `jquery.plax.js`. Adjust script paths to match your project.

## Installation

Include jQuery and plax near the end of your page, before the code that initializes your scene:

```html
<script src="js/jquery.min.js"></script>
<script src="js/jquery.plax.js"></script>
<script src="js/scene.js"></script>
```

Keep a local copy of your dependencies or load them through your existing asset pipeline. Whichever approach you choose, preserve the script order: jQuery first, plax second, scene initialization last.

## Quick start

Create a container and add a few layers:

```html
<div id="scene">
  <img id="sky" src="images/sky.png" alt="">
  <img id="hills" src="images/hills.png" alt="">
  <img id="trees" src="images/trees.png" alt="">
</div>
```

Give the container a defined size and position its children:

```css
#scene {
  position: relative;
  width: 800px;
  height: 400px;
  overflow: hidden;
}

#scene img {
  position: absolute;
  display: block;
}

#sky,
#hills,
#trees {
  top: -20px;
  left: -20px;
}
```

Register the layers, then enable movement:

```javascript
$(function () {
  $('#sky').plaxify({
    xRange: 5,
    yRange: 5
  });

  $('#hills').plaxify({
    xRange: 15,
    yRange: 10
  });

  $('#trees').plaxify({
    xRange: 30,
    yRange: 20
  });

  $.plax.enable();
});
```

Move the pointer across the page to see the layers shift. The sky moves gently, the hills move a little more, and the trees provide the strongest foreground movement.

## Configuring layers

Call `plaxify()` on a jQuery selection to register elements for parallax movement.

```javascript
$('.foreground').plaxify({
  xRange: 30,
  yRange: 15,
  invert: true
});
```

The main options used in these examples are:

| Option | Purpose |
| --- | --- |
| `xRange` | Sets the horizontal movement range. |
| `yRange` | Sets the vertical movement range. |
| `invert` | Reverses the layer’s movement direction. |

Use small ranges for distant details and larger ranges for nearby objects. Set one axis to zero when movement should stay horizontal or vertical.

Inversion can help separate layers visually, but it is easy to overdo. Begin with consistent movement, then reverse individual layers only when it improves the composition.

## Enabling and disabling movement

Once your layers are registered, enable plax:

```javascript
$.plax.enable();
```

To stop its response to movement, disable it:

```javascript
$.plax.disable();
```

These controls are useful when a scene is temporarily hidden, when a user chooses to pause animation, or when your interface changes modes.

Register the scene once during setup and manage its activity deliberately. Avoid repeatedly initializing the same elements inside unrelated event handlers.

## Preparing your artwork

Good parallax starts with a composition designed for movement.

Export foreground, middle-ground, and background artwork as separate assets. Use transparency where layers need to overlap, and preserve a consistent coordinate system so the pieces line up when positioned.

Make moving assets larger than the visible scene. Otherwise, shifting a background can expose an empty strip along an edge. Preview the composition at its movement extremes, checking all four sides.

Keep essential text and controls outside decorative moving layers whenever possible. A heading should remain easy to read, and a button should stay easy to target.

## Responsive layouts

The fixed dimensions in the quick-start example make the setup easy to understand. Adapt them to your layout before shipping.

On smaller screens, reconsider both the scene size and its movement ranges. A movement that feels subtle on a large desktop illustration may feel exaggerated inside a narrow viewport.

Check image scaling, clipping, and layer alignment at each important breakpoint. If the composition loses clarity at small sizes, simplify it or present a static version.

## Accessibility

Treat parallax as an enhancement. Visitors should be able to understand the page and complete its main tasks without movement.

Respect reduced-motion preferences when deciding whether to enable the effect:

```javascript
$(function () {
  var reducedMotion = window.matchMedia &&
    window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;

  if (!reducedMotion) {
    $.plax.enable();
  }
});
```

This example checks the preference during initialization. If your application supports changing motion preferences while it is open, update the scene’s enabled state accordingly.

Use empty alternative text for purely decorative images. Give meaningful images appropriate descriptions, and keep important information available in ordinary page content.

## Performance

A restrained scene usually looks better and costs less to render.

Use a small number of purposeful layers, optimize image dimensions, and avoid unnecessarily large transparent assets. Test alongside the rest of your page: video, scrolling effects, and other animations all share the browser’s resources.

Check performance on the devices your audience actually uses. Reduce complexity when motion becomes uneven.

## Troubleshooting

**Nothing moves:** Check script loading order, confirm your selectors match existing elements, and call `$.plax.enable()` after registration.

**Layers jump or overlap incorrectly:** Review their starting positions, positioning rules, and stacking order.

**Empty edges appear:** Enlarge the artwork, reduce movement ranges, or adjust clipping.

**The effect feels distracting:** Reduce the ranges and remove unnecessary layers. Subtle movement is often enough.

## Contributing

When reporting a problem, include your browser, jQuery version, initialization code, and a small reproducible example. Describe what you expected and what happened.

For changes, keep the scope focused and explain their effect on existing scenes. Include a demonstration when behavior changes visually.
