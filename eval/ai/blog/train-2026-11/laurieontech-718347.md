# Let's talk about Lodash

Few libraries have shaped modern JavaScript as much as Lodash. For years it was the first thing many of us installed on a new project, right after `npm init`. Then the "You Don't Need Lodash" articles started appearing, and the library quietly became a punchline. So where does it actually stand today?

## Why Lodash existed

Early JavaScript had a thin standard library. There was no `Array.prototype.includes`, no `Object.entries`, no optional chaining, no spread operator. Simple tasks like deep-cloning an object, grouping items by a key, or safely reading `a.b.c` without throwing took real effort, and every browser behaved a little differently.

Lodash (a fork of Underscore) filled that gap with a consistent, well-tested toolbox. `_.map`, `_.debounce`, `_.get`, `_.groupBy`: it gave us a shared vocabulary and saved us from rewriting the same helpers in every codebase.

## What the language caught up on

Modern JavaScript absorbed a lot of Lodash's greatest hits:

```js
// Safe property access
const city = user?.address?.city ?? "Unknown";

// Unique values
const unique = [...new Set(items)];

// Flatten
const flat = nested.flat(Infinity);

// Object from entries
const byId = Object.fromEntries(users.map(u => [u.id, u]));

// Deep clone
const copy = structuredClone(original);
```

Each of these used to be a reason to import Lodash. Now they're built in, with no extra bytes shipped to the browser.

## Where Lodash still earns its place

"You don't need Lodash" is true for many one-liners, but not for everything. A few functions remain genuinely useful:

- **`debounce` and `throttle`**: Native alternatives don't exist, and hand-rolled versions are a classic source of subtle bugs (leading/trailing edges, cancellation, `this` binding).
- **`isEqual`**: Deep equality is surprisingly hard to get right. Cycles, `Date`, `Map`, `Set`, typed arrays: Lodash handles them, your quick recursive function probably doesn't.
- **`merge` / `mergeWith`**: Deep merging with customizable behavior is tedious to write correctly.
- **`groupBy`, `keyBy`, `orderBy`**: Some now have native counterparts (`Object.groupBy` is available in current runtimes), but `orderBy` with multiple keys and directions is still more pleasant in Lodash.

The common thread: Lodash is strongest where edge cases are plentiful and correctness matters more than saving a few kilobytes.

## The bundle size concern

The strongest argument against Lodash was always weight. Importing the whole library for one function is wasteful:

```js
// Pulls in far more than you need
import _ from "lodash";

// Better: import only what you use
import debounce from "lodash/debounce";

// Or use the ES module build for tree-shaking
import { debounce } from "lodash-es";
```

With `lodash-es` and a modern bundler, you pay only for what you use. A single `debounce` costs very little. The "Lodash is bloated" claim is mostly a problem of how it's imported, not of the library itself.

## Security and maintenance

Lodash has had prototype pollution vulnerabilities in functions like `merge`, `set`, and `defaultsDeep` over the years. They were patched, but they're a reminder to keep dependencies updated and to be careful when merging untrusted input into objects. That advice applies to any utility library, including your own helpers.

## A practical rule of thumb

Here's how I decide:

1. **Can the platform do it in a line or two?** Use the native version.
2. **Is it a well-known tricky problem** (debounce, deep equality, deep merge)? Use Lodash, imported per function.
3. **Do you need it once?** Consider copying a small, tested implementation rather than adding a dependency.
4. **Is Lodash already in the project?** Don't rip it out just to be fashionable. Migration has a cost, and working code is worth something.

## Final thoughts

Lodash isn't dead, and it isn't essential anymore. It's a mature tool that solved real problems in a less capable era, and it still solves a handful of them better than the alternatives. The healthiest stance is neither nostalgia nor dismissal: reach for the standard library first, and reach for Lodash deliberately when it gives you something the platform doesn't.

What's your take? Have you removed Lodash from a project, or are you still happy with it? Let me know in the comments.
