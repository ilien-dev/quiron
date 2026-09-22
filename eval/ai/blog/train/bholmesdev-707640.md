# Sexy, Accessible Show-Hide Animations in Any Web Framework

Show-hide interactions, accordions, dropdowns, expandable panels, are everywhere in modern UI, and yet they're surprisingly easy to get wrong. You either end up with a jarring instant toggle that feels cheap, or you reach for a heavy animation library just to smoothly expand and collapse a box. Let's fix that. In this post, I'll walk through a technique that gives you smooth, accessible show-hide animations using nothing but CSS, and show how to wire it up in vanilla JavaScript, React, Vue, and Svelte.

## Why This Is Harder Than It Looks

The naive approach to animating a collapsing element is to transition its `height` property from some fixed value down to `0`. The problem is that `height: auto`, the value you actually want most of the time since your content's height is rarely a fixed number, can't be transitioned by CSS. Browsers don't know how to interpolate between a pixel value and `auto`, so the animation either snaps instantly or doesn't animate at all.

There are a few classic workarounds, like measuring the element's scrollHeight in JavaScript and animating to that specific pixel value, but that requires JavaScript to run on every resize and adds complexity that feels disproportionate to the problem. Thankfully, there's a cleaner CSS-only trick using `grid-template-rows`.

## The CSS Trick

Here's the core idea: instead of animating `height` directly, we wrap our content in a grid container and animate the grid track size between `0fr` and `1fr`. Because `fr` units are interpolatable, browsers can smoothly animate between them, effectively animating the content's height without ever needing to know its actual pixel value.

```css
.collapsible {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 300ms ease;
}

.collapsible.expanded {
  grid-template-rows: 1fr;
}

.collapsible > .content {
  overflow: hidden;
}
```

The inner `.content` element needs `overflow: hidden` because a `0fr` row still technically has room to render its content at its natural size unless we clip it. With this in place, toggling the `.expanded` class smoothly animates the panel open and closed, with no JavaScript-measured heights required.

## Respecting Reduced Motion

Before wiring this up anywhere, it's worth handling `prefers-reduced-motion` from the start rather than bolting it on later:

```css
@media (prefers-reduced-motion: reduce) {
  .collapsible {
    transition: none;
  }
}
```

This respects users who have indicated at the OS level that they don't want animated motion, whether for comfort, vestibular sensitivity, or simple preference. It's a small addition that makes a real difference for a meaningful chunk of your users.

## Making It Accessible

The animation is only half the story. For a show-hide interaction to be genuinely accessible, the trigger and the content need to be properly associated for screen reader and keyboard users. At minimum, the toggle button needs `aria-expanded`, and it's worth associating the button with the content it controls via `aria-controls`:

```html
<button aria-expanded="false" aria-controls="panel-1" id="trigger-1">
  Toggle details
</button>
<div id="panel-1" class="collapsible" role="region" aria-labelledby="trigger-1">
  <div class="content">
    <p>Here's the content that gets revealed.</p>
  </div>
</div>
```

`aria-expanded` needs to be kept in sync with the actual state via JavaScript, toggling between `"true"` and `"false"` whenever the panel opens or closes. This lets assistive technology announce the current state to users who can't see the visual animation at all.

## Vanilla JavaScript Implementation

```js
const trigger = document.getElementById('trigger-1');
const panel = document.getElementById('panel-1');

trigger.addEventListener('click', () => {
  const expanded = trigger.getAttribute('aria-expanded') === 'true';
  trigger.setAttribute('aria-expanded', String(!expanded));
  panel.classList.toggle('expanded');
});
```

Simple, framework-free, and it works anywhere.

## React Implementation

```jsx
function Collapsible() {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <button
        aria-expanded={expanded}
        aria-controls="panel-1"
        onClick={() => setExpanded(!expanded)}
      >
        Toggle details
      </button>
      <div
        id="panel-1"
        className={`collapsible ${expanded ? 'expanded' : ''}`}
        role="region"
      >
        <div className="content">
          <p>Here's the content that gets revealed.</p>
        </div>
      </div>
    </>
  );
}
```

The logic maps almost one to one onto the vanilla version. React just handles the class toggling and attribute syncing declaratively through state instead of imperative DOM manipulation.

## Vue Implementation

```vue
<template>
  <button
    :aria-expanded="expanded"
    aria-controls="panel-1"
    @click="expanded = !expanded"
  >
    Toggle details
  </button>
  <div
    id="panel-1"
    class="collapsible"
    :class="{ expanded }"
    role="region"
  >
    <div class="content">
      <p>Here's the content that gets revealed.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const expanded = ref(false);
</script>
```

Vue's reactive `ref` and class bindings make this almost as terse as the React version, with the same underlying CSS doing all the animation work.

## Svelte Implementation

```svelte
<script>
  let expanded = false;
</script>

<button
  aria-expanded={expanded}
  aria-controls="panel-1"
  on:click={() => (expanded = !expanded)}
>
  Toggle details
</button>
<div
  id="panel-1"
  class="collapsible"
  class:expanded
  role="region"
>
  <div class="content">
    <p>Here's the content that gets revealed.</p>
  </div>
</div>
```

Svelte's `class:expanded` shorthand makes conditional classes especially clean, but functionally it's doing exactly the same thing as every other implementation here.

## Why This Approach Wins

Across every framework, the actual animation logic lives entirely in CSS. The JavaScript in each version is only responsible for toggling a boolean and keeping `aria-expanded` in sync, nothing more. That separation matters. It means the animation stays performant, since the browser can optimize CSS-driven layout transitions far better than JavaScript-driven ones, and it means the accessibility semantics don't get tangled up with animation timing logic. You could swap out any of these frameworks for another one entirely and the CSS wouldn't need to change at all.

## Wrapping Up

Smooth show-hide animations don't require a bulky animation library or fragile height-measuring JavaScript. A single CSS trick using `grid-template-rows`, combined with a few `aria` attributes kept in sync by whatever framework you're using, gets you an animation that's both genuinely accessible and pleasant to use. Try dropping this pattern into your next accordion, dropdown, or expandable panel, and see how far a little bit of well-placed CSS can go.
