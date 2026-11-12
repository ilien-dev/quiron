# Intro to Regex for Web Developers

Regular expressions have a reputation: powerful, cryptic, and a little scary. But if you write for the web, you're already surrounded by text that needs validating, searching, and reshaping. Regex is the tool built for that job. Let's make it approachable.

## What Is a Regex?

A regular expression (regex) is a pattern that describes a set of strings. You use it to ask questions like "does this look like an email?" or "find every hex color in this stylesheet."

In JavaScript, you write one between slashes:

```js
const pattern = /cat/;
pattern.test("concatenate"); // true
pattern.test("dog");         // false
```

`test()` returns a boolean. That's the simplest use, and it's often all you need.

## The Building Blocks

**Character classes** match one character from a set:

- `\d` matches a digit (`0-9`)
- `\w` matches a letter, digit, or underscore
- `\s` matches whitespace
- `.` matches any character except a newline
- `[abc]` matches `a`, `b`, or `c`
- `[^abc]` matches anything *but* those

**Quantifiers** say how many times:

- `*` zero or more
- `+` one or more
- `?` zero or one
- `{3}` exactly three, `{2,4}` between two and four

**Anchors** pin a match to a position:

- `^` start of string
- `$` end of string
- `\b` word boundary

Combine them and you get something useful:

```js
const zip = /^\d{5}$/;
zip.test("90210");  // true
zip.test("9021");   // false
zip.test("902101"); // false
```

Without the anchors, `"902101"` would pass, because it *contains* five digits. Forgetting `^` and `$` is one of the most common beginner bugs.

## Groups and Captures

Parentheses group parts of a pattern and capture what they match:

```js
const date = /(\d{4})-(\d{2})-(\d{2})/;
const [, year, month, day] = "2026-11-12".match(date);
console.log(year, month, day); // 2026 11 12
```

Named groups make this more readable:

```js
const date = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const { year, month, day } = "2026-11-12".match(date).groups;
```

## Flags

Flags go after the closing slash and change behavior:

- `g` finds all matches, not just the first
- `i` ignores case
- `m` makes `^` and `$` work per line

```js
"Red, red, RED".match(/red/gi); // ["Red", "red", "RED"]
```

## Search and Replace

`String.prototype.replace()` becomes much more powerful with regex. Here's a quick slug generator:

```js
const slugify = (title) =>
  title
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "") // drop punctuation
    .replace(/\s+/g, "-");        // spaces to hyphens

slugify("Intro to Regex for Web Developers!");
// "intro-to-regex-for-web-developers"
```

You can also reuse captures in the replacement with `$1`, `$2`, and so on:

```js
"Doe, Jane".replace(/(\w+), (\w+)/, "$2 $1"); // "Jane Doe"
```

## Real-World Uses on the Web

- **Form validation:** check phone numbers, postal codes, and usernames
- **Routing:** frameworks match URL patterns like `/users/:id`
- **Parsing:** pull query values or IDs out of strings
- **Editor search:** VS Code's find-and-replace supports regex, which is great for refactoring

## Pitfalls to Avoid

**Don't validate emails with a monster regex.** The full email spec is notoriously complicated. A simple sanity check like `/^\S+@\S+\.\S+$/` is fine on the client; confirm real addresses by sending a message.

**Beware greedy matching.** Quantifiers grab as much as they can:

```js
"<b>bold</b> and <i>italic</i>".match(/<.+>/);
// matches the whole string
"<b>bold</b> and <i>italic</i>".match(/<.+?>/g);
// ["<b>", "</b>", "<i>", "</i>"]
```

Adding `?` makes a quantifier lazy.

**Don't parse HTML with regex.** For anything beyond trivial cases, use the DOM or a parser.

**Watch for catastrophic backtracking.** Nested quantifiers like `/(a+)+$/` can freeze on certain inputs. This matters most when running regex on untrusted user input on a server.

## Tools for Learning

- [regex101.com](https://regex101.com) explains your pattern piece by piece
- [regexr.com](https://regexr.com) offers a visual playground and a cheat sheet
- MDN's Regular Expressions guide is an excellent reference

## Wrapping Up

You don't need to memorize everything. Learn the handful of building blocks above (classes, quantifiers, anchors, groups, and flags) and you'll handle the vast majority of real tasks. Start small, test your patterns in a playground, and add comments when a pattern gets complicated. Future you will be grateful.

What's the most useful regex you've written? Share it in the comments!
