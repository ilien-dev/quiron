Every project needs a disclosure widget sooner or later: an accordion, a "read more" panel, a FAQ, a mobile nav. Most of us have built one that looked great and was broken in ways we couldn't see. Keyboard users tabbed into invisible links, screen readers announced content that wasn't on screen, and the animation ignored `prefers-reduced-motion`.

This post builds one that is smooth, accessible, and **independent of any framework**. The trick is to let CSS do all the animating and let your framework do the one thing it's good at: flip a piece of state.

## Why this is harder than it looks

You can't transition to or from `display: none`, and you can't (historically) transition `height: auto`. So people reach for:

- **`max-height: 1000px` hacks.** The timing is wrong because the animation runs against the fake max, not the real height.
- **JS that measures `scrollHeight`.** This works, but it's brittle, and it breaks when content reflows.
- **Conditional rendering (`v-if`, `{open && <Panel/>}`).** The element vanishes instantly, so there's no exit animation.

We can do better with modern CSS.

## Step 1: Markup that's accessible before it's pretty

Start with semantics. Animation is decoration, and the structure has to work without it.

```html
<div class="disclosure">
  <h3>
    <button
      type="button"
      aria-expanded="false"
      aria-controls="panel-1"
      id="trigger-1"
    >
      Shipping details
    </button>
  </h3>

  <div class="collapse" id="panel-1" data-open="false" role="region" aria-labelledby="trigger-1">
    <div class="collapse__inner">
      <p>Orders ship within 2 business days...</p>
      <a href="/shipping">Full policy</a>
    </div>
  </div>
</div>
```

A few deliberate choices here:

- A real `<button>` inside a heading. You get keyboard support (Enter and Space) and focus styles for free, and screen reader users can navigate by heading.
- `aria-expanded` on the button communicates state. `aria-controls` links it to the panel.
- The panel has two wrappers. The outer one animates, and the inner one clips. You'll see why in a moment.

(If you only need a simple disclosure, the native `<details>`/`<summary>` is great and I'll mention it at the end. But a custom button gives you full control over animation across all browsers today.)

## Step 2: Animate height without knowing the height

The cleanest cross-browser technique is to animate `grid-template-rows` from `0fr` to `1fr`. Grid tracks *can* be interpolated, and `1fr` resolves to the content's natural height.

```css
.collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 350ms var(--ease-out);
}

.collapse[data-open="true"] {
  grid-template-rows: 1fr;
}

.collapse__inner {
  overflow: hidden;
  min-height: 0; /* lets the grid item shrink below its content size */
}
```

`min-height: 0` and `overflow: hidden` on the inner element are the whole trick. Without them, the grid item refuses to shrink smaller than its content.

Define the easing once. This curve starts fast and settles gently, which is what makes it feel premium rather than mechanical:

```css
:root {
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}
```

At this point it animates, but it's not accessible yet.

## Step 3: Hide collapsed content from everyone, not just the eyes

Here's the bug in most "animated accordion" demos. A collapsed panel has zero visible height, but its links and buttons are still focusable and still read by assistive tech. A keyboard user tabs into a void.

The fix is `visibility: hidden` on the collapsed state. It removes content from both the tab order and the accessibility tree. But if you apply it immediately, you'd cut off the closing animation. So we delay it until the transition finishes:

```css
.collapse {
  display: grid;
  grid-template-rows: 0fr;
  visibility: hidden;
  transition:
    grid-template-rows 350ms var(--ease-out),
    visibility 0s linear 350ms; /* flip to hidden AFTER the collapse */
}

.collapse[data-open="true"] {
  grid-template-rows: 1fr;
  visibility: visible;
  transition:
    grid-template-rows 350ms var(--ease-out),
    visibility 0s linear 0s; /* flip to visible immediately */
}
```

`visibility` interpolates discretely, and when either end of the transition is `visible`, it stays visible for the whole duration. So the panel remains visible while closing and then disappears right at the end. It works in every browser, with no JS timers.

## Step 4: Add the "sexy"

Height alone is fine. Height plus a coordinated fade and slight movement is what makes people say "ooh."

```css
.collapse__inner > * {
  opacity: 0;
  transform: translateY(-6px);
  transition:
    opacity 250ms ease,
    transform 350ms var(--ease-out);
}

.collapse[data-open="true"] .collapse__inner > * {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 80ms; /* content arrives just after the space opens */
}
```

The delay on opening matters: the container starts making room, then the content settles in. On close, there's no delay, so content leaves quickly and the space follows. Small asymmetries like this are what separate polished motion from generic motion.

You can also stagger children with a custom property:

```css
.collapse__inner > * {
  transition-delay: calc(var(--i, 0) * 40ms);
}
```

Set `style="--i: 1"`, `--i: 2`, and so on, from your template or loop.

## Step 5: Respect reduced motion

Some users get nauseous or distracted from animation. Honoring their OS setting takes a few lines:

```css
@media (prefers-reduced-motion: reduce) {
  .collapse,
  .collapse__inner > * {
    transition-duration: 0.01ms !important;
    transition-delay: 0s !important;
    transform: none;
  }
}
```

Note that we keep the state change and drop the motion. The panel still opens and closes, just instantly. Reducing motion doesn't mean removing function.

## Step 6: Wire it to any framework

Because the CSS reads a single attribute, `data-open`, every framework integration is nearly identical: **render the element always, and bind the attribute to state.** Never conditionally render the panel, or you'll kill the exit animation.

### Vanilla JS

```js
document.querySelectorAll('.disclosure').forEach((root) => {
  const button = root.querySelector('button[aria-expanded]');
  const panel = root.querySelector('.collapse');

  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!open));
    panel.dataset.open = String(!open);
  });
});
```

### React

```jsx
import { useId, useState } from 'react';

export function Disclosure({ title, children }) {
  const [open, setOpen] = useState(false);
  const id = useId();

  return (
    <div className="disclosure">
      <h3>
        <button
          type="button"
          id={`${id}-trigger`}
          aria-expanded={open}
          aria-controls={`${id}-panel`}
          onClick={() => setOpen((o) => !o)}
        >
          {title}
        </button>
      </h3>
      <div
        className="collapse"
        id={`${id}-panel`}
        role="region"
        aria-labelledby={`${id}-trigger`}
        data-open={open}
      >
        <div className="collapse__inner">{children}</div>
      </div>
    </div>
  );
}
```

### Vue 3

```vue
<script setup>
import { ref, useId } from 'vue';
defineProps({ title: String });
const open = ref(false);
const id = useId();
</script>

<template>
  <div class="disclosure">
    <h3>
      <button
        type="button"
        :id="`${id}-trigger`"
        :aria-expanded="open"
        :aria-controls="`${id}-panel`"
        @click="open = !open"
      >
        {{ title }}
      </button>
    </h3>
    <div
      class="collapse"
      :id="`${id}-panel`"
      role="region"
      :aria-labelledby="`${id}-trigger`"
      :data-open="open"
    >
      <div class="collapse__inner"><slot /></div>
    </div>
  </div>
</template>
```

Use `v-show`-style thinking, not `v-if`: the element must stay in the DOM.

### Svelte 5

```svelte
<script>
  let { title, children } = $props();
  let open = $state(false);
  const id = $props.id();
</script>

<div class="disclosure">
  <h3>
    <button
      type="button"
      id="{id}-trigger"
      aria-expanded={open}
      aria-controls="{id}-panel"
      onclick={() => (open = !open)}
    >
      {title}
    </button>
  </h3>
  <div class="collapse" id="{id}-panel" role="region"
       aria-labelledby="{id}-trigger" data-open={open}>
    <div class="collapse__inner">{@render children()}</div>
  </div>
</div>
```

The CSS is identical in all four. That's the payoff of keeping the animation in the stylesheet: you write it once, and it travels with you across projects, framework migrations, and design systems.

## The modern shortcuts (use as progressive enhancement)

Newer CSS can simplify parts of this. Check current browser support before relying on any of it.

**`interpolate-size`** lets you animate to intrinsic sizes like `auto` directly:

```css
:root { interpolate-size: allow-keywords; }

.panel { height: 0; overflow: hidden; transition: height 350ms var(--ease-out); }
.panel[data-open="true"] { height: auto; }
```

**`@starting-style` with `transition-behavior: allow-discrete`** lets you animate `display` changes, which is ideal for elements that truly need to leave layout, such as toasts, popovers, and dialogs:

```css
.toast {
  transition: opacity 250ms, display 250ms allow-discrete;
}
.toast[hidden] { display: none; opacity: 0; }
@starting-style { .toast:not([hidden]) { opacity: 0; } }
```

Because these degrade to "instant," they make good enhancements layered on the grid technique rather than replacements for it.

For the native route, `<details>` plus `::details-content` can now be animated, and `<details name="group">` gives you exclusive accordions with no JavaScript. If your browser targets allow it, it's the least code of all.

## Quick checklist

Before you ship, verify:

- [ ] The trigger is a real `<button>` with `aria-expanded` and `aria-controls`
- [ ] Collapsed content is `visibility: hidden` (not focusable, not announced)
- [ ] The panel stays in the DOM so exit animations can run
- [ ] `prefers-reduced-motion` removes the motion but keeps the behavior
- [ ] You can operate it with only a keyboard, and focus is never lost
- [ ] You've tried it once with a screen reader (VoiceOver, NVDA, or Narrator)

## Wrapping up

The pattern is small:

1. State toggles one attribute.
2. CSS animates `grid-template-rows`, opacity, and transform.
3. A delayed `visibility` flip keeps hidden content out of the tab order and accessibility tree.
4. A reduced-motion query respects the user.

Beautiful and accessible aren't in tension here. The accessible version is the same code with a few extra lines, and those lines are what make it work for everyone.

If you have a trickier case, like nested accordions or animating content that loads asynchronously, drop it in the comments and I'll dig in.

---

I wrote this at roughly 1,400 words. I haven't run the snippets in a browser, so test them in your target browsers before publishing, especially the `interpolate-size` and `::details-content` notes, since support changes quickly. I set `published: false` in the front matter so it lands as a draft on dev.to.
