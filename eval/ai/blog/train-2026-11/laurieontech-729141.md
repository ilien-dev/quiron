If you've written JavaScript for a while, you've probably needed the *last* item that matches a condition. Maybe it's the most recent failed payment, the latest log entry for a user, or the final step in a workflow that completed. Until recently, the built-in tools for this were awkward. ES2023 added two methods that fix that: `Array.prototype.findLast()` and `Array.prototype.findLastIndex()`.

## The problem with the old approaches

Before these methods, you had a few options, and none were great.

You could reverse the array and call `find()`:

```js
const lastError = errors.reverse().find(e => e.level === "error");
```

This works, but `reverse()` mutates the original array. If you forget that and reuse `errors` later, you'll get a surprising order. You could copy first with `[...errors].reverse()`, but that's an extra allocation and one more thing to remember.

You could write a manual loop:

```js
let lastError;
for (let i = errors.length - 1; i >= 0; i--) {
  if (errors[i].level === "error") {
    lastError = errors[i];
    break;
  }
}
```

This is correct, but it's five lines of boilerplate for a simple question, and it's easy to get the index bounds wrong.

## Enter `findLast`

`findLast()` works like `find()`, but it searches from the end of the array toward the start. It takes the same callback signature, `(element, index, array)`, and returns the first match it finds while walking backward, or `undefined` if nothing matches.

```js
const orders = [
  { id: 1, status: "shipped" },
  { id: 2, status: "pending" },
  { id: 3, status: "shipped" },
  { id: 4, status: "pending" },
];

const lastShipped = orders.findLast(o => o.status === "shipped");
// { id: 3, status: "shipped" }
```

The original array is untouched, and the code says exactly what you mean.

## Enter `findLastIndex`

`findLastIndex()` is to `findLast()` what `findIndex()` is to `find()`. It returns the index of the last matching element, or `-1` if there isn't one.

```js
const lastShippedIndex = orders.findLastIndex(o => o.status === "shipped");
// 2

orders.findLastIndex(o => o.status === "cancelled");
// -1
```

This is handy when you need to splice, slice, or update the element in place:

```js
const i = orders.findLastIndex(o => o.status === "pending");
if (i !== -1) {
  orders[i] = { ...orders[i], status: "shipped" };
}
```

## A few things to know

- **Callbacks run from the end.** If the callback has side effects, such as logging, the calls happen in reverse order. Don't rely on that for anything else.
- **Typed arrays support these methods too.** `Int32Array`, `Float64Array`, and the other typed array types also have `findLast()` and `findLastIndex()`.
- **Browser and runtime support is broad.** They're available in all current major browsers and in Node.js 18 and later.
- **TypeScript needs the right lib.** Set `"lib": ["es2023"]` (or a later target) in your `tsconfig.json`, or the types won't be recognized.

## When to use them

Use `findLast()` when you want a value and `findLastIndex()` when you want a position. Both are clearer than reversing, copying, or hand-rolling a loop, and neither changes the array you started with. If your codebase targets older runtimes, a small polyfill or a transpiler setting can cover the gap, but for most modern projects you can use them directly.

Small methods like these don't change what you can build, but they remove a common bit of friction. The next time you catch yourself writing `.reverse().find(...)`, reach for `findLast()` instead.
