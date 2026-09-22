# React 18: Terms and Functionality

React 18 is here, and with it comes a wave of new vocabulary. Concurrent rendering, automatic batching, transitions, Suspense on the server... If you've been reading release notes and feeling like you need a glossary, this post is for you.

Let's walk through the key terms and what they actually do.

## Concurrent React

This is the big one. **Concurrency** isn't a feature you turn on by itself; it's a new behind-the-scenes mechanism that lets React prepare multiple versions of the UI at the same time.

Before React 18, rendering was synchronous. Once React started rendering an update, nothing could interrupt it until it finished. With concurrent rendering, React can start rendering an update, pause it, work on something more urgent, and then come back. It can even throw away a render that's no longer needed.

The important thing to know: concurrent rendering is only used when you opt into features that rely on it, like transitions. Your existing code keeps working as before.

## `createRoot`

To use React 18's new features, you need the new root API:

```jsx
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

The old `ReactDOM.render` still works, but it runs your app in legacy mode, which means you won't get concurrent features. Switching to `createRoot` is the first step for most upgrades.

## Automatic batching

**Batching** is when React groups multiple state updates into a single re-render for better performance.

React already batched updates inside event handlers. But updates inside promises, `setTimeout`, or native event handlers weren't batched:

```jsx
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React 17: two renders
  // React 18: one render
}, 1000);
```

In React 18, with `createRoot`, all updates are batched automatically, no matter where they come from. If you really need to opt out, there's `flushSync`.

## Transitions

A **transition** marks an update as non-urgent. Urgent updates are things like typing or clicking, where users expect an instant response. Transition updates are things like filtering a big list, where a small delay is fine.

```jsx
import { useTransition } from 'react';

const [isPending, startTransition] = useTransition();

function handleChange(e) {
  setInput(e.target.value);          // urgent
  startTransition(() => {
    setSearchQuery(e.target.value);  // can wait
  });
}
```

React will keep the input responsive and render the filtered results when it can. If the user types again, React abandons the stale render. `isPending` lets you show a loading hint.

There's also a standalone `startTransition` function for cases where you can't use the hook.

## `useDeferredValue`

Similar idea, different angle. `useDeferredValue` gives you a version of a value that "lags behind" during urgent updates:

```jsx
const deferredQuery = useDeferredValue(query);
```

It's useful when you don't control the code that sets the state but still want to defer expensive rendering based on it.

## Suspense improvements

**Suspense** lets you declare a loading state for part of your component tree:

```jsx
<Suspense fallback={<Spinner />}>
  <Comments />
</Suspense>
```

React 18 expands Suspense to work with server rendering and transitions. On the server, it enables **streaming HTML** and **selective hydration**: React can send the page in chunks and hydrate the parts the user interacts with first, rather than waiting for everything.

## Strict Mode changes

In development, Strict Mode now mounts, unmounts, and remounts components to surface effects that don't clean up properly. If you see effects firing twice in dev, this is why. It's preparing your code for future features that may preserve state across unmounts.

## New hooks for libraries

React 18 also ships `useId` for generating stable unique IDs (great for accessibility attributes), plus `useSyncExternalStore` and `useInsertionEffect`, which are mainly for library authors.

## Wrapping up

The short version:

- **Concurrency** is the engine
- **`createRoot`** turns it on
- **Automatic batching** gives you fewer renders for free
- **Transitions** and **`useDeferredValue`** let you mark work as non-urgent
- **Suspense** now works on the server with streaming

Most apps can upgrade with minimal changes and adopt the new features gradually. Now you have the vocabulary to do it.
