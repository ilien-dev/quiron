React 18 changed how React renders more than it changed how you write components. Most existing code keeps working, but the release brought a set of new terms that come up in documentation, code reviews, and job interviews. This post explains what each one means and when it matters.

## Concurrent Rendering

**Concurrent rendering** is the foundation of React 18. Before it, rendering was synchronous: once React started an update, it ran to completion and blocked the main thread until it finished.

With concurrent rendering, React can **interrupt, pause, resume, or abandon** a render. If a user types while React is rendering a large list, React can handle the keystroke first and come back to the list afterward.

Concurrency isn't a feature you turn on. It's a capability that other features use, and you only get it when you use those features.

## The New Root API: `createRoot`

To use React 18 features, you replace the legacy `ReactDOM.render` with `createRoot`:

```jsx
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

For server-rendered apps, `hydrateRoot` replaces `ReactDOM.hydrate`. If you skip this migration, your app runs in legacy mode and the new behavior stays off.

## Automatic Batching

**Batching** means React groups several state updates into one re-render. React 17 did this only inside React event handlers. Updates inside promises, `setTimeout`, or native event listeners each caused a separate render.

React 18 batches **everywhere**:

```jsx
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React 18: one re-render. React 17: two.
}, 1000);
```

If you need to opt out, `flushSync` forces an immediate update.

## Transitions

A **transition** marks an update as non-urgent. Urgent updates, like typing or clicking, should feel instant. Transition updates, like filtering a big list, can wait.

```jsx
import { useTransition } from 'react';

const [isPending, startTransition] = useTransition();

function handleChange(e) {
  setInput(e.target.value);          // urgent
  startTransition(() => {
    setQuery(e.target.value);        // can be interrupted
  });
}
```

`isPending` lets you show a loading hint while the transition renders. If you're outside a component, a standalone `startTransition` function is also available.

## `useDeferredValue`

`useDeferredValue` works like a transition, but you apply it to a **value** instead of wrapping the update. It's useful when you don't control the code that sets the state:

```jsx
const deferredQuery = useDeferredValue(query);
// Render expensive results with deferredQuery
```

React first renders with the old value and then updates to the new one in the background.

## Suspense on the Server

`<Suspense>` lets you declare a fallback while part of the tree isn't ready yet. React 18 extends it to server rendering with two features:

- **Streaming SSR**: the server sends HTML in chunks (via `renderToPipeableStream`), so fast parts of the page show up without waiting for slow ones.
- **Selective Hydration**: React hydrates sections independently and prioritizes the parts the user is interacting with.

The result is a page that becomes visible and interactive sooner.

## New Hooks

- **`useId`**: generates unique IDs that stay stable between server and client. It's handy for `htmlFor` and ARIA attributes.
- **`useSyncExternalStore`**: lets external stores (Redux, Zustand, and similar) subscribe safely under concurrent rendering, without "tearing," where different parts of the UI show inconsistent values.
- **`useInsertionEffect`**: aimed at CSS-in-JS library authors. It injects styles before layout effects run.

## Stricter Strict Mode

In development, `<StrictMode>` now **mounts, unmounts, and remounts** each component. This double-invoked effect surfaces cleanup bugs early and prepares components for future features that preserve state across remounts. If an effect breaks when it runs twice, it's missing a cleanup function.

## Wrapping Up

React 18 is mostly about **scheduling**: deciding what to render and when. The key points:

1. Switch to `createRoot` to enable the new behavior.
2. Automatic batching comes for free.
3. Use transitions and `useDeferredValue` to keep heavy UI responsive.
4. Suspense plus streaming makes SSR faster.
5. Make sure your effects clean up after themselves.

Learn these terms and the rest of the concurrent React ecosystem, including React 19 and Server Components, will make a lot more sense.

*What React 18 feature has made the biggest difference in your projects? Share it in the comments.*
