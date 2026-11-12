# React 18 Alpha is out! Now what?

*Written from the perspective of the June 2021 alpha announcement.*

React 18 Alpha has landed, and you might already be wondering how much of your app needs rewriting.

Take a breath. You don’t need to drop everything, replace your components, or spend the weekend untangling dependencies.

This release gives the community an early look at React’s next chapter: more responsive interfaces, fewer unnecessary renders, and better server rendering. For now, the most useful thing you can do is understand what’s coming and decide whether experimenting makes sense for you.

Let’s walk through it.

**First, who is this alpha for?**

The initial audience is library maintainers. The React team wants feedback from the people building the routers, state managers, and component libraries that applications depend on.

If you’re learning React or shipping an application, there’s no immediate migration deadline. The alpha is an opportunity to explore, and its APIs and behavior can still change. Keep production applications on a stable release while you experiment separately. The [official announcement](https://react.dev/blog/2021/06/08/the-plan-for-react-18) explains the rollout and its intended audience.

**The big idea: concurrent rendering**

Think about a search box that filters a large list.

Typing should feel instant. Updating thousands of results can take longer. When those tasks compete, users notice the lag in the input before they appreciate your beautifully rendered results.

Concurrent rendering gives React more flexibility when scheduling rendering work. It can prepare an update, pause that work for something more urgent, and continue afterward.

This doesn’t mean your JavaScript suddenly runs across multiple threads. It means React can organize rendering around the interaction happening right now.

**Try the alpha in a small project**

At the time of the announcement, you can install the preview with:

```bash
npm install react@alpha react-dom@alpha
```

Then try the new root API. In the initial alpha, that looks like this:

```jsx
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

const root = ReactDOM.createRoot(
  document.getElementById("root")
);

root.render(<App />);
```

That historical import matters: alpha examples may differ from documentation published later.

The new root enables React 18’s new behavior. Keeping the older rendering API lets you compare behavior while working through an upgrade. See the [working group’s root API discussion](https://github.com/reactwg/react-18/discussions/5) for details.

**Automatic batching means less rendering work**

React already batches multiple state updates inside React event handlers. React 18 expands that behavior, with the new root, to updates inside promises, timeouts, and native event handlers.

For example:

```jsx
fetchSomething().then(() => {
  setCount(count => count + 1);
  setLoading(false);
});
```

Previously, these updates could cause separate renders. Automatic batching lets React handle them together, reducing unnecessary work.

You usually won’t need to redesign a component to benefit. However, code that assumes the DOM changes immediately after a state update deserves attention during testing. The [batching discussion](https://github.com/reactwg/react-18/discussions/21) includes examples and compatibility considerations.

**Transitions help prioritize interactions**

The new `startTransition` API lets you mark an update as less urgent:

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

Here, the input updates immediately, while rendering results for `searchQuery` can yield to more typing.

The callback runs immediately; React treats the state updates scheduled inside it as transitions. It won’t make an expensive calculation inside that callback disappear. The benefit comes from making the resulting rendering interruptible. The [transition introduction](https://github.com/reactwg/react-18/discussions/41) explains that distinction.

**Server rendering is changing, too**

React 18 also introduces a Suspense-based server rendering architecture.

Instead of making an entire page wait for its slowest section, React can stream ready content and fill in other sections later. Selective hydration also helps parts of the page become interactive without waiting for everything else.

Framework integration will matter here. Follow your framework’s guidance as support develops. The [architecture overview](https://github.com/reactwg/react-18/discussions/37) explains how these pieces fit together.

So, what should you actually do this week?

Pick one small interaction, try the alpha in a branch, and compare the experience. Check your dependencies, record unexpected behavior, and share reproducible issues.

If you maintain a library, compatibility testing now can help many developers later. If you build applications, understanding these ideas is already useful preparation.

And if your current app works well? Keep shipping. There’s room to learn React 18 without turning an alpha announcement into an emergency.
