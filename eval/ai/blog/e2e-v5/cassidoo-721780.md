# React 18 Alpha is out! Now what?

The React 18 alpha came out on June 8th, and you can read the [announcement post](https://reactjs.org/blog/2021/06/08/the-plan-for-react-18.html) for the full plan. Most of the gains need very little code change on your end, which is nice.

To try it:

```bash
npm install react@alpha react-dom@alpha
```

Before you get too excited (I say this as someone who is very excited): it's going to be months before this hits beta, and longer than that before it's stable. The [roadmap](https://github.com/reactwg/react-18/discussions/9) has the details. Play with it on a side project or a branch, but keep production on stable React for now.

## The new Root API

This is the part you'll actually have to touch. `ReactDOM.render` is now called the "Legacy Root API." It works the same way it did in React 17, and it'll be deprecated eventually. Here's the new one:

```jsx
import ReactDOM from "react-dom";
import App from "./App";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(<App />);
```

A couple of other things changed with it. `hydrate` is gone (it's now an option you pass to `createRoot`), and so is the render callback. For all of these, the React Working Group has [migration examples](https://github.com/reactwg/react-18/discussions/5).

For client-only React apps, the switch to the new root is... the whole upgrade. That's it! React 18 also batches more state updates automatically. Updates in timeouts and promises can get combined into one render instead of several:

```jsx
setTimeout(() => {
  setCount((count) => count + 1);
  setEnabled((enabled) => !enabled);
}, 1000);
```

## Suspense, for real this time

Suspense has technically been around since React 16, but only partially, and honestly it's been kind of confusing. In React 18 it's fully supported, and I am so excited about this.

There's one behavior change to know about: nothing inside a Suspense boundary renders until the data resolves. You can read the working group's [explanation](https://github.com/reactwg/react-18/discussions/7), and there's a [CodeSandbox](https://codesandbox.io/s/romantic-architecture-ht3qi?file=/src/App.js) where you can see it in action.

## Concurrent features you can opt into

Everything else new is opt-in:

- [`startTransition`](https://github.com/reactwg/react-18/discussions/41)
- `useDeferredValue`
- `SuspenseList`
- [Selective hydration for server-side rendering](https://github.com/reactwg/react-18/discussions/37)

Not all of these are documented yet, so expect some digging. Here's what `startTransition` looks like, where typing in the input is urgent and updating the search results can wait:

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

What I like most about all of this is that you can adopt the features piece by piece. Switch the root, get the benefits, and then pull in transitions or the Suspense changes when you actually have a use for them.

If you want to follow along or ask questions, the [React 18 Working Group discussions](https://github.com/reactwg/react-18/discussions) are the place to be!
