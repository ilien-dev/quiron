# React 18 Alpha is out! Now what?

React 18 is in alpha. It brings a new rendering engine, automatic batching, better server-side rendering, and APIs meant to keep your UI responsive while expensive updates run.

That sounds exciting, but what does it actually mean for React developers right now?

## First: don't upgrade production yet

An alpha is an early preview, and it isn't ready for production. APIs may change and the docs are still being written, and third-party libraries might not work with it yet.

So treat React 18 Alpha as an invitation to play around. Try it in a small side project or run your component library against it, or make a separate branch of an app you already have, but don't ship it to users unless you're fine dealing with things that break.

The alpha is most useful for library authors. If they test now, the React team and the people who maintain the ecosystem have time to fix compatibility problems before the stable release.

## Concurrent rendering is the big idea

Traditionally, once React starts rendering an update, it keeps going until that render is done. If the update is expensive, the browser might not be able to respond to user input right away, and typing and clicking start to feel sluggish.

Concurrent rendering lets React interrupt that work. React can start an update and pause it when something more urgent comes in, then pick it back up later. It can also throw away a render that's out of date before it ever reaches the DOM.

Everything doesn't suddenly run in parallel, though. JavaScript is still JavaScript, and React just gets better at deciding what work to do first.

You get concurrent behavior when your app switches to the new root API:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

The old `ReactDOM.render` API is still there during the transition, so you can upgrade a bit at a time.

## Automatic batching means fewer renders

React already batches some state updates, mostly inside event handlers. React 18 does it in more places.

Updates that happen inside promises, timeouts or native event handlers can now be batched too:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

Before React 18, these two updates could cause two separate renders. With automatic batching, React can combine them into one.

For most apps this should make things faster without any code changes. It's still worth testing, especially if some of your code (by accident, usually) relies on state being rendered right away between updates.

## Transitions separate urgent and non-urgent work

Some updates need to feel instant: when someone types into an input, the character should show up with no delay. Other updates, like recalculating a big filtered list, can wait a moment.

React 18 adds transitions so you can say which is which:

```jsx
import { startTransition } from "react";

function handleChange(event) {
  const value = event.target.value;

  setInputValue(value);

  startTransition(() => {
    setSearchQuery(value);
  });
}
```

Here, updating the input is urgent and updating the search results is a transition, so if the user types another character, React can interrupt the slower work.

There's also a `useTransition` hook that tells you whether a transition is still pending, so you can show some feedback while React gets the next screen ready.

## Suspense is growing up

Suspense first came out alongside `React.lazy`, to show fallback content while code loads. In React 18 it does a lot more, mostly on the server side.

The new server renderer can stream HTML. Instead of waiting for the whole page to be ready, the server can send finished sections early, and React can hydrate parts of the page as the code for each part shows up.

That could make server-rendered apps show up and respond to the user a lot faster, especially on slow connections.

How this looks for you will depend a lot on your framework. If you use Next.js, Remix or another React framework, expect its maintainers to hand you the setup they recommend. You probably won't be wiring up streaming yourself.

## What should you do now?

Most developers don't need to rewrite anything. React 18 is built so you can adopt it gradually, and your existing components should keep working.

A reasonable plan:

1. Read the upgrade guidance and follow the working group discussions.
2. Test the alpha in a non-critical project.
3. Check for warnings caused by the new root API or stricter development checks.
4. Verify important third-party dependencies.
5. Experiment with transitions only where expensive updates affect responsiveness.
6. Report reproducible problems instead of building permanent workarounds for alpha behavior.

To me, the most exciting part of React 18 is the scheduling underneath all these new hooks and options. React is getting better at knowing which work is urgent and which can wait, and at keeping the page responsive while both kinds of work happen.

For now, go explore. Just keep production on stable React.
