# Intro to regex for web developers

Regular expressions (regex) have a reputation for being confusing and a little terrifying. If you've ever seen a pattern like `^(?:[a-z0-9]+(?:[._-][a-z0-9]+)*)@...` and immediately closed the tab, you're not alone. But once you understand the basics, regex becomes one of the most useful tools a web developer has.

In this post I'll walk through the fundamentals, with examples you'll actually use in day-to-day web development.

## What is regex?

A regular expression is a pattern used to match character combinations in strings. You don't search for an exact string. You describe the *shape* of what you're looking for, like "a sequence of digits" or "a word starting with a capital letter."

Regex shows up all over web development: form validation, search, string parsing, find-and-replace in your editor, routing patterns and more.

## Basic syntax

In JavaScript, you can create a regex pattern two ways.

```js
const regex1 = /hello/;
const regex2 = new RegExp('hello');
```

Both of these match the literal string "hello" anywhere in a piece of text.

```js
/hello/.test('hello world'); // true
/hello/.test('goodbye');     // false
```

## Special characters

Most of the power of regex comes from special characters. They stand for patterns, and they do not match themselves as literal text. Here are the ones you will see most:

- `.` matches any single character.
- `\d` matches any digit (0-9).
- For any word character (letters, digits and `_`), use `\w`.
- `\s` matches any whitespace character.
- The start of a string is `^`.
- And `$` is the end of a string.

For example, to accept exactly three numbers and nothing else.

```js
/^\d{3}$/.test('123'); // true
/^\d{3}$/.test('12');  // false
```

## Quantifiers

These characters control how many times something can appear.

- `*`: zero or more
- `+`: one or more
- `?`: zero or one
- `{n}`: exactly n times
- `{n,m}`: between n and m times

```js
/colou?r/.test('color');  // true
/colou?r/.test('colour'); // true
```

Here the `?` makes the "u" optional, so the pattern matches both the American and the British spelling.

## Character classes

Sometimes you want to match one character from a specific set. That is what square brackets are for.

```js
/[aeiou]/.test('hello'); // true — matches the 'e' or 'o'
```

A character class can also be negated with `^` inside the brackets.

```js
/[^0-9]/.test('abc'); // true — matches any non-digit character
```

## A practical example: email validation

I'll put this together with something you'll actually use, a (simplified) email validator:

```js
const emailRegex = /^[\w.-]+@[\w.-]+\.\w+$/;

emailRegex.test('hello@example.com'); // true
emailRegex.test('not-an-email');      // false
```

Here's how I'd read it, piece by piece.
- `^[\w.-]+` is one or more word characters, dots or hyphens at the start.
- Then `@` is a literal @ symbol.
- `[\w.-]+` is the domain name.
- And `\.\w+$` is a dot followed by the TLD (like .com or .org).

Keep in mind this pattern is simplified. Real-world email validation is notoriously tricky, and most production apps rely on more reliable libraries or on server-side verification.

## Using regex with string methods

You can use regex with more than `.test()`. It pairs well with common string methods too.

```js
'Hello World'.replace(/o/g, '0'); // "Hell0 W0rld"

'one,two,three'.split(/,/); // ["one", "two", "three"]

'The year is 2024'.match(/\d+/); // ["2024"]
```

Note the `g` flag in the `replace` example. It stands for "global," which means it replaces *all* matches and not only the first one. Other useful flags include `i` (case-insensitive) and `m` (multiline).

## Tools to help you learn

Regex can get complicated fast, especially once nested groups and lookaheads are involved. A couple of tools make my life easier.

- [regex101.com](https://regex101.com) lets you test patterns interactively, with explanations.
- Your browser's dev console is a quick way to test small patterns on the fly.

## Wrapping up

Regex doesn't need to be scary. Start with the basics (literal matches, character classes and quantifiers) and build up from there. Once you're comfortable, I bet you'll start noticing places to use regex everywhere, like validating form inputs, parsing URLs and cleaning up messy data.

It is a skill that I think pays off the more you use it, so don't be afraid to experiment.
