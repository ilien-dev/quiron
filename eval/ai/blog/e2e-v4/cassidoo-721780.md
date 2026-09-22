# React 18 Alpha is out! Now what?

React 18 is in alpha! It comes with a new rendering engine, automatic batching, better server-side rendering, and some new APIs for keeping your interface responsive while expensive updates are going on.

Sounds fun. But what does it actually mean for you, a React developer, today?

## First things first: don't upgrade production yet

An alpha is an early preview. It is not ready for production. The APIs might change, the docs are still being written, and your third-party libraries might not work with it yet.

So think of it as an invitation to play around. Try it in a small side project, run your component library against it, or make a separate branch of an app you already have. Just don't ship it to users unless you're fine dealing with things behaving weirdly.

If you write libraries, this is especially for you! Testing now gives the React team and the people who maintain the ecosystem time to fix compatibility problems before the stable release.

## Concurrent rendering is the big one

The biggest change in React 18 is concurrent rendering. Up until now, once React starts rendering an update, it keeps going until that render is done. If the update is expensive, the browser might not be able to respond to the user right away, and typing, clicking and navigating start to feel sluggish.

With concurrent rendering, React can interrupt that work. It can start an update, pause it when something more urgent comes up, and pick it back up later. It can even throw away a render that's out of date before it ever gets committed to the DOM.

(This doesn't mean everything suddenly runs in parallel. JavaScript is still JavaScript! React just gets better at scheduling work by priority.)

You get concurrent behavior when your app switches to the new root API:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

The old `ReactDOM.render` API sticks around during the transition, so you can upgrade bit by bit.

## Automatic batching (fewer renders!)

React already batches some state updates, mostly the ones inside event handlers. React 18 does it in more places, so updates that happen inside promises, timeouts or native event handlers can get batched too:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

Before, each of those updates could cause its own render. Automatic batching lets React combine them into one.

For most apps this should make things faster without you changing any code. I'd still test it though, especially if some of your code accidentally depends on state being rendered right away between updates.

## Transitions: urgent vs. not urgent

Some updates need to happen immediately. When someone types into an input, the character they typed should show up right away. Other updates, like recalculating a big filtered list, can wait a little.

React 18 adds transitions so you can tell React which is which:

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

Updating the input is urgent. Updating the search results is a transition, so if the user types another character, React can interrupt the slower work.

There's also a `useTransition` hook that tells you whether a transition is still pending, so you can show the user something useful while React gets the next screen ready.

## Suspense is growing up

Suspense first showed up alongside `React.lazy`, for showing fallback content while code loads. In React 18 it does a lot more, especially for server-side rendering.

The new architecture supports streaming HTML from the server. So instead of waiting for the whole page to be ready the server can send the sections that are done first, and React can hydrate parts of the page as their code arrives. That could make server-rendered apps show up and become interactive a lot faster, especially on slow connections.

How this looks for you will depend a lot on your framework. If you use Next.js, Remix, or another React framework, expect the maintainers to give you the recommended way to set it up, so you won't be building the whole streaming setup yourself.

## So what should you do now?

Probably not much! Most of you won't need to rewrite anything. React 18 is meant to be adopted gradually, and your existing components should keep working.

If you want a plan, here's what I'd do:

1. Read the upgrade guidance and follow the working group discussions.
2. Test the alpha in a project that doesn't matter much.
3. Look for warnings from the new root API or the stricter development checks.
4. Check that your important third-party dependencies still work.
5. Only try transitions where expensive updates are making things feel slow.
6. Report problems you can reproduce, instead of building permanent workarounds for alpha behavior.

Honestly the part I'm most excited about isn't any one hook or config option. It's the scheduling underneath all of them: React is learning which work is urgent, which work can wait, and how to keep the page responsive while both are going on.

For now go play with it and keep production on stable React. Until next time!
