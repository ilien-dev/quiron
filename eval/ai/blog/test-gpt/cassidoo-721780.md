# React 18 Alpha is out! Now what?

React 18 has entered alpha, bringing a new rendering engine, automatic batching, improved server-side rendering, and APIs designed to keep interfaces responsive during expensive updates.

That sounds exciting—but what does it actually mean for React developers today?

## First: don’t upgrade production yet

An alpha release is an early preview, not a production-ready version. APIs may change, documentation is still evolving, and third-party libraries might not be compatible.

React 18 Alpha is best treated as an invitation to experiment. Try it in a small side project, test your component library, or create a separate branch of an existing application. Avoid shipping it to users unless you are comfortable dealing with unstable behavior.

The alpha is especially valuable for library authors. Testing now gives the React team and ecosystem maintainers time to resolve compatibility problems before the stable release.

## Concurrent rendering is the big idea

The most important change in React 18 is concurrent rendering.

Traditionally, once React starts rendering an update, it keeps working until that render finishes. If the update is expensive, the browser may be unable to respond immediately to user input. That can make typing, clicking, and navigation feel sluggish.

Concurrent rendering allows React to interrupt rendering work. React can begin an update, pause it when something more urgent happens, and continue later. It can also abandon an outdated render before committing it to the DOM.

This does not mean everything suddenly runs in parallel. JavaScript is still JavaScript. Instead, React becomes better at scheduling work according to priority.

Concurrent behavior is enabled when an application adopts the new root API:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

The existing `ReactDOM.render` API remains available during the transition, allowing applications to upgrade gradually.

## Automatic batching means fewer renders

React already batches some state updates, particularly inside event handlers. React 18 expands this behavior.

Updates triggered inside promises, timeouts, or native event handlers can now be batched too:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

Previously, these updates could cause separate renders. With automatic batching, React can combine them into a single render.

For most applications, this should improve performance without requiring code changes. It is still worth testing carefully, especially if existing code accidentally relies on state being rendered immediately between updates.

## Transitions separate urgent and non-urgent work

Some updates need immediate feedback. When a user types into an input, the entered character should appear without delay. Other updates—such as recalculating a large filtered list—can wait briefly.

React 18 introduces transitions to express that difference:

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

Here, updating the input is urgent. Updating the search results is a transition. React can interrupt the slower work if the user types another character.

There is also a `useTransition` hook for tracking whether a transition is pending, making it possible to display useful feedback while React prepares the next screen.

## Suspense is growing up

Suspense was originally introduced alongside `React.lazy` for displaying fallback content while code loads. React 18 expands its role, particularly in server-side rendering.

The new architecture supports streaming HTML from the server. Instead of waiting for an entire page to become ready, the server can send completed sections earlier. React can then hydrate parts of the interface as their code becomes available.

This could significantly improve how quickly server-rendered applications become visible and interactive, especially on slow connections.

The details will depend heavily on frameworks. If you use Next.js, Remix, or another React framework, expect its maintainers to provide the preferred integration rather than implementing the complete streaming setup yourself.

## What should you do now?

Most developers do not need to rewrite anything. React 18 is intended to support gradual adoption, and existing components should continue working.

A sensible plan is:

1. Read the upgrade guidance and follow the working group discussions.
2. Test the alpha in a non-critical project.
3. Check for warnings caused by the new root API or stricter development checks.
4. Verify important third-party dependencies.
5. Experiment with transitions only where expensive updates affect responsiveness.
6. Report reproducible problems instead of building permanent workarounds for alpha behavior.

The most exciting part of React 18 is not a single hook or configuration option. It is the scheduling foundation underneath them. React is gaining a better understanding of which work is urgent, which work can wait, and how to keep the interface responsive while both are happening.

For now, explore—but keep production on stable React.