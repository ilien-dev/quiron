# React 18 Alpha is out! Now what?

A new React release is coming, and the word *concurrent* is making the rounds again. If your first reaction is “Do I need to rewrite my app?” take a breath.

The React team’s answer is no. React 18 is designed for gradual adoption, and its alpha was initially published to help library maintainers test their integrations and share feedback. If you build applications, this is a good time to learn and experiment—not a reason to rush an alpha into production. [React’s announcement](https://react.dev/blog/2021/06/08/the-plan-for-react-18) lays out the plan.

So what’s changing, and what should you do next?

> **A note on timing:** React 18 was released as stable in March 2022. This post looks back at the alpha announcement and the ideas it introduced.

## First, what does concurrent rendering mean?

React normally renders an update and then applies the result to the screen. Concurrent rendering gives React more flexibility while preparing an update: it can pause work, continue it later, or abandon it if a more urgent update arrives.

Imagine typing into a search box that filters a large list. Updating the text input should feel immediate. Rendering thousands of matching rows can be less urgent. React 18 introduces tools that let you communicate that distinction.

This is a change in how React can schedule rendering, but it isn’t an all-or-nothing switch you have to flip across your app. Concurrent rendering is activated by features that use it, so you can adopt those features gradually. Your components still need to follow React’s rules, including keeping rendering free of side effects. [The React working group explains the adoption strategy.](https://github.com/reactwg/react-18/discussions/64)

## Automatic batching: fewer unnecessary renders

Batching means grouping multiple state updates into one render. React already batched updates inside React event handlers, but updates in places such as promises and timers didn’t always receive the same treatment.

With React 18’s new root API, those updates can be batched automatically:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setOpen((open) => !open);
  // React can process these updates in one render.
}, 1000);
```

That can mean less rendering work without adding special code. It’s still worth testing any code that assumes the DOM has updated immediately after a state change. The [upgrade guide](https://react.dev/blog/2022/03/08/react-18-upgrade-guide#automatic-batching) covers the behavior and the rare cases where you might need to opt out.

## Transitions: keep urgent updates responsive

The new transition API lets you mark an update as non-urgent. Here’s a simplified search example:

```jsx
import { startTransition, useState } from "react";

function Search() {
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");

  function handleChange(event) {
    const value = event.target.value;

    setInput(value); // Update the text field immediately.

    startTransition(() => {
      setQuery(value); // Update the results as a transition.
    });
  }

  return (
    <>
      <input value={input} onChange={handleChange} />
      <SearchResults query={query} />
    </>
  );
}
```

If another keystroke arrives while React is rendering the results, React can interrupt that work and prioritize the input. A transition won’t make an expensive calculation magically faster, but it can make the interaction feel more responsive. For pending indicators, there’s also `useTransition`.

## Suspense meets server rendering

React 18 also brings improvements to server rendering with Suspense. The goal is to let a server stream parts of a page as they’re ready, rather than making the entire response wait for every section.

For example, a page could send its main layout while a slower section is still loading. Suspense boundaries give React places to show fallback content until the corresponding content is ready.

This area is especially relevant if you maintain a framework or server-rendered app. Check your framework’s support and guidance before changing your rendering setup; integration details matter. The [React 18 release post](https://react.dev/blog/2022/03/29/react-v18#suspense-in-data-frameworks) explains how the pieces fit together.

## What should you do now?

If you’re looking at the alpha announcement from an application developer’s perspective, here’s a practical path:

1. **Keep production on a stable release.** Alpha APIs and behavior can change.
2. **Try an isolated experiment.** Create a small branch or demo and explore a transition with a deliberately slow results list.
3. **Audit assumptions.** Look for side effects during rendering and code that depends on exactly when updates reach the DOM.
4. **Check your dependencies.** Library and framework compatibility matters as much as your own code.
5. **Follow the discussion.** The public [React 18 working group](https://github.com/reactwg/react-18/discussions) has useful explanations from the people building and testing these features.

If you’re upgrading a real app today, use the stable release and its upgrade guide rather than historical alpha installation instructions. For a client-rendered app moving to React 18, that includes reviewing the switch from `ReactDOM.render` to `createRoot`.

The exciting part of React 18 is the set of options it opens up. You can start with a normal upgrade, learn where your app feels slow, and introduce concurrent features where they improve the experience. What will you try first?
