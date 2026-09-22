# React 18 Alpha is out! Now what?

React 18 is in alpha. It brings a new rendering engine, automatic batching, better server-side rendering, and APIs that keep the UI responsive while an expensive update runs.

That sounds exciting. But what does it mean for us as React developers right now?

## First, don't upgrade production yet

An alpha is an early preview. It isn't ready for production: APIs may change, the docs are still being written, and third-party libraries might not work with it.

I'd treat React 18 Alpha as an invitation to play around. Try it in a small side project, test your component library against it, or make a separate branch of an app you already have. Don't ship it to users unless you're fine dealing with things that break.

The alpha matters most for library authors. If they test now, the React team and the ecosystem maintainers get time to fix compatibility problems before the stable release.

## Concurrent rendering is the big idea

The biggest change in React 18 is concurrent rendering. Until now, once React started rendering an update it kept going until that render was done. If the update was expensive, the browser might not be able to respond to input right away, and typing, clicking and navigating could feel sluggish.

With concurrent rendering React can interrupt its rendering work. React can start an update, pause the update when something more urgent comes in, and pick the update back up later. It can also throw away a render that's out of date before it ever gets committed to the DOM.

This doesn't mean everything suddenly runs in parallel. JavaScript is still JavaScript. What changes is that React gets better at scheduling work by priority.

You get concurrent behavior when your app switches to the new root API:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

The old `ReactDOM.render` API sticks around during the transition, so apps can upgrade a bit at a time.

## Automatic batching means fewer renders

React already batches some state updates, mostly inside event handlers. React 18 batches updates in more places. Updates that happen inside promises, timeouts or native event handlers can now be batched too:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

Before, each of these updates could cause its own render. With automatic batching, React can batch the updates into one render.

For most of our apps this should make things faster without any code changes. I'd still test batching carefully, especially if your code accidentally depends on state being rendered right away between updates.

## Transitions split urgent work from work that can wait

Some updates need to happen right away. When someone types into an input, the character they typed should show up right away. Other updates, like recalculating a big filtered list, can wait a moment.

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

Here, updating the input is urgent, and updating the search results is a transition. If the user types another character, React can interrupt the slower work.

There's also a `useTransition` hook that tells you whether a transition is pending. We can use it to show some feedback while React gets the next screen ready.

## Suspense is growing up

Suspense first shipped next to `React.lazy`, as a way to show fallback content while code loads. In React 18 it does a lot more, especially for server-side rendering.

The new architecture supports streaming HTML from the server. The server doesn't have to wait for the whole page to be ready. The server can send the finished sections of the page early, and React can hydrate parts of the UI as their code arrives.

I think that could make server-rendered apps show up and become interactive a lot faster, especially on slow connections.

How this works in practice will depend heavily on your framework. If you use Next.js, Remix or another React framework, expect the framework's maintainers to give you the integration they recommend. You probably won't have to wire up the whole streaming setup yourself.

## What should you do now?

Most of us won't need to rewrite anything. React 18 is meant to be adopted gradually, and your existing components should keep working.

Here's a plan that makes sense to me:

1. Read the upgrade guidance and follow the working group discussions.
2. Test the alpha in a project that isn't critical.
3. Look for warnings from the new root API or the stricter checks in development.
4. Check your important third-party dependencies.
5. Try transitions only where expensive updates hurt responsiveness.
6. Report problems you can reproduce, and don't build permanent workarounds for how the alpha behaves.

For me the most exciting part of React 18 is the scheduling foundation under all the new hooks and options. React is learning which work is urgent and which work can wait, and how to keep the UI responsive while both are going on. For now, go explore, and keep production on stable React.
