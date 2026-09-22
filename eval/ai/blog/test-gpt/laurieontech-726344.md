# `at` coming soon to ECMAScript

Accessing an array element by its index is one of JavaScript’s simplest operations:

```js
const languages = ["JavaScript", "TypeScript", "Rust"];

languages[0]; // "JavaScript"
languages[1]; // "TypeScript"
```

Accessing an element relative to the end of an array, however, has always been a little less elegant:

```js
languages[languages.length - 1]; // "Rust"
languages[languages.length - 2]; // "TypeScript"
```

The upcoming `at()` method gives us a cleaner way to express the same operation:

```js
languages.at(-1); // "Rust"
languages.at(-2); // "TypeScript"
```

## Positive and negative indexes

`at()` accepts an integer representing the position to retrieve. Positive values work much like bracket notation:

```js
const colors = ["red", "green", "blue"];

colors.at(0); // "red"
colors.at(1); // "green"
colors.at(2); // "blue"
```

The useful addition is support for negative indexes. A negative value counts backward from the end of the collection:

```js
colors.at(-1); // "blue"
colors.at(-2); // "green"
colors.at(-3); // "red"
```

If the requested position is outside the collection, the method returns `undefined`:

```js
colors.at(10);  // undefined
colors.at(-10); // undefined
```

This makes code that works with the final items of a collection shorter and, more importantly, easier to read.

Compare these two expressions:

```js
const lastColor = colors[colors.length - 1];
const lastColor = colors.at(-1);
```

The second version communicates its intention immediately.

## More than arrays

`at()` is not limited to regular arrays. It is also available for strings:

```js
const message = "hello";

message.at(0);  // "h"
message.at(-1); // "o"
```

This is especially convenient because ordinary string bracket access does not interpret negative indexes as positions from the end:

```js
message[-1];    // undefined
message.at(-1); // "o"
```

Typed arrays support the method as well:

```js
const values = new Uint8Array([10, 20, 30]);

values.at(-1); // 30
```

That gives arrays, strings, and typed arrays a consistent API for relative indexing.

## Why not change bracket notation?

It may seem natural to make `array[-1]` return the final element. JavaScript cannot safely introduce that behavior, though, because property access and array indexing share the same syntax.

When we write this:

```js
array[-1]
```

JavaScript treats `"-1"` as an object property name. Existing programs may already use negative-number-like properties for their own purposes. Changing their meaning would risk breaking code on the web.

A separate method adds negative indexing without changing the behavior of existing programs.

## A useful detail

Because `at()` is a normal method, it works nicely with expressions:

```js
const index = -1;
const item = colors.at(index);
```

It also avoids repeating the collection when retrieving an element relative to its length:

```js
getResults()[getResults().length - 1]; // Calls getResults() twice
getResults().at(-1);                   // Calls it once
```

Of course, bracket notation is not going away. It remains concise and familiar for ordinary positive indexes:

```js
colors[0];
```

`at()` simply gives JavaScript a clearer tool when negative or computed relative indexes are involved.

It is a small addition, but those are often the best language features: easy to learn, immediately readable, and useful in everyday code. Soon, getting the last item in a collection can finally be written exactly as we mean it:

```js
const lastItem = items.at(-1);
```