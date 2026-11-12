# `at` coming soon to ECMAScript

*Update: `at()` arrived in ECMAScript 2022. If you’re using a modern JavaScript runtime, you may already have it. Here’s what it does and why it’s useful.*

How often have you written something like this?

```js
const colors = ["red", "green", "blue"];

const lastColor = colors[colors.length - 1];

console.log(lastColor); // "blue"
```

There’s nothing wrong with it. But for such a common operation, it feels like a lot of ceremony: mention the array twice, find its length, and subtract one.

The `at()` method gives us a shorter way to get an element relative to the end:

```js
const lastColor = colors.at(-1);

console.log(lastColor); // "blue"
```

That `-1` means “start at the end and move back one position.” It’s a small addition, but one you may find yourself reaching for often.

## Counting from either end

Like bracket notation, `at()` accepts zero-based positive indexes:

```js
const colors = ["red", "green", "blue"];

colors.at(0); // "red"
colors.at(1); // "green"
```

The interesting part is what happens with negative indexes:

```js
colors.at(-1); // "blue"
colors.at(-2); // "green"
colors.at(-3); // "red"
```

This can make code especially readable when the position matters more than the array’s length. For example, suppose a list contains the steps a user has visited:

```js
const visitedSteps = ["account", "profile", "review"];

const currentStep = visitedSteps.at(-1);
const previousStep = visitedSteps.at(-2);

console.log(currentStep);  // "review"
console.log(previousStep); // "profile"
```

The method also works nicely when an array is returned from another operation:

```js
const latestTag = "javascript,web,ecmascript"
  .split(",")
  .at(-1);

console.log(latestTag); // "ecmascript"
```

## Why not just use `[-1]`?

If you’ve used Python, you might expect this to work:

```js
const colors = ["red", "green", "blue"];

console.log(colors[-1]); // undefined
```

In JavaScript, bracket notation accesses object properties. A negative number inside the brackets refers to a property named `"-1"`; it doesn’t automatically count backward from the end.

That distinction matters because you *can* assign such a property:

```js
colors[-1] = "purple";

console.log(colors[-1]);   // "purple"
console.log(colors.at(-1)); // "blue"
```

The new method provides relative indexing without changing what existing bracket notation means. The [TC39 proposal](https://github.com/tc39/proposal-relative-indexing-method) has more background on the design.

## Arrays aren’t the only option

`at()` is also available on strings and typed arrays:

```js
"JavaScript".at(-1); // "t"

const bytes = new Uint8Array([10, 20, 30]);
bytes.at(-1); // 30
```

There’s one detail to remember with strings: `at()` returns a UTF-16 **code unit**, so it doesn’t necessarily return a complete emoji or other character represented by multiple code units. If you need to work with Unicode code points, converting the string with `Array.from()` first can help:

```js
const message = "Hi 👋";

console.log(Array.from(message).at(-1)); // "👋"
```

Even code points don’t always equal what a reader sees as one character, though. For more complex text, consider `Intl.Segmenter`.

## A couple of practical details

If the requested position is outside the array, `at()` returns `undefined`:

```js
const colors = ["red", "green", "blue"];

colors.at(10); // undefined
colors.at(-4); // undefined
[].at(-1);     // undefined
```

And `at()` reads a value; it doesn’t give you a position you can assign to. To replace the last item, you can still use bracket notation:

```js
colors[colors.length - 1] = "navy";
```

The method is part of [ECMAScript 2022](https://tc39.es/ecma262/2023/multipage/), and [MDN’s compatibility table](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/at) can help you check the runtimes you support. For older environments, consider a polyfill.

Next time you need the last item in an array, give `.at(-1)` a try. Your future self may appreciate the simpler read.
