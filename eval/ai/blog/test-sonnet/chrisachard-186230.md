# Intro to Regex for Web Developers

Regular expressions — or regex — have a reputation for being confusing, cryptic, and vaguely terrifying. If you've ever seen a pattern like `^(?:[a-z0-9]+(?:[._-][a-z0-9]+)*)@...` and immediately closed the tab, you're not alone. But once you understand the basics, regex becomes one of the most useful tools in a web developer's toolbox.

In this post, we'll walk through the fundamentals of regex, with examples you'll actually use in day-to-day web development.

## What Is Regex?

A regular expression is a pattern used to match character combinations in strings. Instead of searching for an exact string, you describe the *shape* of what you're looking for — things like "a sequence of digits" or "a word starting with a capital letter."

Regex shows up everywhere in web development: form validation, search functionality, string parsing, find-and-replace in your editor, routing patterns, and more.

## Basic Syntax

In JavaScript, you can create a regex pattern two ways:

```js
const regex1 = /hello/;
const regex2 = new RegExp('hello');
```

Both of these match the literal string "hello" anywhere in a piece of text.

```js
/hello/.test('hello world'); // true
/hello/.test('goodbye');     // false
```

## Special Characters

The real power of regex comes from special characters that represent patterns rather than literal text:

- `.` — matches any single character
- `\d` — matches any digit (0-9)
- `\w` — matches any word character (letters, digits, underscore)
- `\s` — matches any whitespace character
- `^` — matches the start of a string
- `$` — matches the end of a string

For example, to match a string that's exactly three digits:

```js
/^\d{3}$/.test('123'); // true
/^\d{3}$/.test('12');  // false
```

## Quantifiers

Quantifiers control how many times something can appear:

- `*` — zero or more
- `+` — one or more
- `?` — zero or one
- `{n}` — exactly n times
- `{n,m}` — between n and m times

```js
/colou?r/.test('color');  // true
/colou?r/.test('colour'); // true
```

Here, the `?` makes the "u" optional, so it matches both American and British spellings.

## Character Classes

Sometimes you want to match one character from a specific set. That's where square brackets come in:

```js
/[aeiou]/.test('hello'); // true — matches the 'e' or 'o'
```

You can also negate a character class with `^` inside the brackets:

```js
/[^0-9]/.test('abc'); // true — matches any non-digit character
```

## A Practical Example: Email Validation

Let's put this together with something you'll actually use — a (simplified) email validator:

```js
const emailRegex = /^[\w.-]+@[\w.-]+\.\w+$/;

emailRegex.test('hello@example.com'); // true
emailRegex.test('not-an-email');      // false
```

Breaking this down:
- `^[\w.-]+` — one or more word characters, dots, or hyphens at the start
- `@` — a literal @ symbol
- `[\w.-]+` — the domain name
- `\.\w+$` — a dot followed by the TLD (like .com or .org)

Keep in mind this is a simplified pattern — real-world email validation is notoriously tricky, and most production apps rely on more robust libraries or server-side verification.

## Using Regex with String Methods

Regex isn't just for `.test()`. It pairs well with common string methods too:

```js
'Hello World'.replace(/o/g, '0'); // "Hell0 W0rld"

'one,two,three'.split(/,/); // ["one", "two", "three"]

'The year is 2024'.match(/\d+/); // ["2024"]
```

Note the `g` flag in the `replace` example — that stands for "global," meaning it replaces *all* matches instead of just the first one. Other useful flags include `i` (case-insensitive) and `m` (multiline).

## Tools to Help You Learn

Regex can get complicated fast, especially with nested groups and lookaheads. A couple of tools that make life easier:

- [regex101.com](https://regex101.com) — lets you test patterns interactively with explanations
- Your browser's dev console — a quick way to test small patterns on the fly

## Wrapping Up

Regex doesn't need to be scary. Start with the basics — literal matches, character classes, and quantifiers — and build up from there. Once you get comfortable, you'll start noticing opportunities to use regex everywhere: validating form inputs, parsing URLs, cleaning up messy data, and much more.

It's a skill that pays dividends the more you use it, so don't be afraid to experiment.
