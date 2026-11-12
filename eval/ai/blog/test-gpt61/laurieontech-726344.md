# `at` coming soon to ECMAScript

*Editor’s note: This post uses a pre-release perspective to match the title. `at()` subsequently became part of [ECMAScript 2022](https://tc39.es/ecma262/2022/multipage/indexed-collections.html#sec-array.prototype.at).*

Getting the last item in a JavaScript array should be a small task. Usually, it looks like this:

```js
const colors = ["red", "green", "blue"];

const lastColor = colors[colors.length - 1];
// "blue"
```

It works, but there’s some repetition. We name the array twice, read its length, and subtract one just to say “give me the last item.”

The upcoming `at()` method gives us a shorter way to express that:

```js
const lastColor = colors.at(-1);
// "blue"
```

That negative number is the interesting part: `at()` lets us count backward from the end.

**How the indexing works**

Positive indexes behave as you’d expect. Zero selects the first item, one selects the second, and so on.

Negative indexes start at the other end: `-1` selects the last item, `-2` selects the second-to-last item.

```js
const colors = ["red", "green", "blue"];

colors.at(0);  // "red"
colors.at(1);  // "green"
colors.at(-1); // "blue"
colors.at(-2); // "green"
```

You can think of a negative index as adding that number to the collection’s length. For an array with three elements, `at(-1)` reads the element at index two.

There’s no wraparound. If the resulting index falls outside the array, the method returns `undefined`. An empty array also returns `undefined`. These bounds checks are part of the [specified algorithm](https://tc39.es/ecma262/2022/multipage/indexed-collections.html#sec-array.prototype.at).

```js
colors.at(99);  // undefined
colors.at(-99); // undefined
[].at(-1);     // undefined
```

**Why can’t we just use `array[-1]`?**

If you’ve used Python, you might have tried this already:

```js
colors[-1]; // undefined
```

In JavaScript, bracket notation accesses properties. Here, `-1` becomes the property key `"-1"`; it doesn’t mean “the last array element.”

That property can even exist independently:

```js
const values = [10, 20, 30];

values[-1] = "a separate property";

values[-1];    // "a separate property"
values.at(-1); // 30
```

Changing bracket notation would change existing behavior. A separate method adds relative indexing while preserving those property-access rules. The [TC39 proposal](https://github.com/tc39/proposal-relative-indexing-method) explains this design choice.

**A nicer ending for method chains**

The improvement becomes especially useful when the array comes from another operation:

```js
const filename = "images/profile/avatar.png"
  .split("/")
  .at(-1);

// "avatar.png"
```

Without `at()`, you might introduce a temporary variable or use `slice(-1)[0]`.

The latter works, but creates an intermediate array. `at()` directly expresses that you want one element. It also reads without removing the item, so it serves a different purpose from `pop()`, which mutates the array.

For example, inspecting the latest event shouldn’t consume it:

```js
const events = ["connected", "message", "disconnected"];

const latestEvent = events.at(-1);

console.log(latestEvent); // "disconnected"
console.log(events.length); // 3
```

**Strings and typed arrays get it too**

The proposal also covers strings and typed arrays:

```js
"JavaScript".at(-1); // "t"

const bytes = new Uint8Array([12, 24, 48]);
bytes.at(-1); // 48
```

One detail matters for text: string indexing operates on UTF-16 code units. An emoji can occupy more than one code unit, so `at()` doesn’t necessarily return a complete visible character. The [V8 introduction](https://v8.dev/features/at-method) calls out this limitation.

For older environments, check that the method exists before relying on it:

```js
typeof Array.prototype.at === "function";
```

`at()` is a small addition, but it addresses a familiar bit of friction. The next time you need the final item in a collection, `at(-1)` makes that intention easy to read.
