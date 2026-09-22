# React 18 Alpha is out! Now what?

React 18 is in alpha. It brings a new rendering engine, automatic batching, better server-side rendering, and new APIs to keep the UI responsive while expensive updates run.

That sounds exciting, but what does it mean for React developers right now?

## First: don't upgrade production yet

An alpha is an early preview. It isn't ready for production. APIs may change, the docs are still being written, and third-party libraries might not work with it yet.

I'd treat it as an invitation to play. Try it in a small side project, or run your component library against it, or make a separate branch of an app you already have. Don't ship it to users unless you're fine dealing with things that break.

If you maintain a library, the alpha is especially worth your time. Testing now gives the React team and the people who maintain the ecosystem time to fix compatibility problems before the stable release.

## Concurrent rendering is the big idea

The biggest change in React 18 is concurrent rendering.

Up to now, once React starts rendering an update, it keeps going until that render is done. If the update is expensive, the browser may not be able to respond to the user right away, and typing, clicking and navigating can feel slow.

With concurrent rendering, React can interrupt that work. It can start an update, pause it when something more urgent comes in, and pick it back up later. It can also throw away a render that's out of date before it ever gets to the DOM.

That doesn't mean everything suddenly runs in parallel. JavaScript is still JavaScript. What changes is that React gets better at deciding what to work on first.

You get the concurrent behavior when your app switches to the new root API:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

`ReactDOM.render` is still there during the transition, so you can move over gradually.

## Automatic batching means fewer renders

React already batches some state updates, mostly inside event handlers. React 18 does it in more places. Updates inside promises, timeouts and native event handlers can now be batched too:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

Before, these two updates could cause two separate renders. With automatic batching React can combine them into one.

For most apps this should make things faster without any code changes. It's still worth testing, though, especially if some of your code relies (maybe by accident) on the state being rendered in between updates.

## Transitions: urgent and not urgent

Some updates need feedback right away. When someone types into an input, the character they typed should show up with no delay. Other updates, like recalculating a big filtered list, can wait a little.

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

Updating the input is urgent here. Updating the search results is a transition, and React can interrupt that slower work if the user types another character.

There's also a `useTransition` hook that tells you whether a transition is pending. You can use it to show the user something useful while React gets the next screen ready.

## Suspense is growing up

Suspense first shipped alongside `React.lazy`, to show fallback content while code loads. React 18 gives it a bigger job, mostly in server-side rendering.

The new architecture can stream HTML from the server. The server doesn't have to wait for the whole page to be ready; it can send the finished parts earlier. Then React can hydrate each part of the page as its code arrives.

This could make a big difference to how fast server-rendered apps show up and become usable, especially on slow connections. How it works for you will depend a lot on your framework, though. If you use Next.js, Remix or another React framework, expect the people who maintain it to hand you the integration, so you won't be wiring up streaming yourself.

## So what should you do now?

Most of us don't need to rewrite anything. React 18 is meant to be adopted gradually, and the components you have should keep working. Here's the plan I'd follow:

1. Read the upgrade guidance and follow the working group discussions.
2. Test the alpha in a project that doesn't matter much.
3. Look for warnings from the new root API or the stricter development checks.
4. Check the third-party dependencies you really rely on.
5. Only try transitions where expensive updates are making the UI slow.
6. Report problems you can reproduce, and don't build permanent workarounds for alpha behavior.

For now, go play with it, and keep production on stable React.
