# Demystifying GREP

If you've spent any time in a terminal, you've seen `grep`. It looks cryptic, it's usually pasted from Stack Overflow, and it works just well enough that most of us never learn it properly. Let's fix that.

## What grep actually is

`grep` stands for **g**lobal **r**egular **e**xpression **p**rint. It comes from the old `ed` editor command `g/re/p`: search globally for a regular expression and print matching lines. That's the whole job. Give it a pattern and some text, and it prints the lines that match.

```bash
grep "error" app.log
```

That prints every line in `app.log` containing `error`. Everything else is refinement.

## The flags worth memorizing

You don't need all of them. These cover most daily use:

| Flag | Meaning |
|------|---------|
| `-i` | Ignore case |
| `-n` | Show line numbers |
| `-r` | Recurse into directories |
| `-v` | Invert: show lines that *don't* match |
| `-c` | Count matching lines |
| `-l` | List only filenames with matches |
| `-w` | Match whole words only |
| `-A N` / `-B N` / `-C N` | Show N lines after / before / around a match |

A few combinations you'll use constantly:

```bash
# Find a function definition across a project, with line numbers
grep -rn "function handleLogin" src/

# Which files mention a config key?
grep -rl "API_TIMEOUT" .

# Show 3 lines of context around each error
grep -C 3 "Exception" server.log

# Everything except comments
grep -v "^#" config.conf
```

## Regular expressions, without the fear

By default, `grep` uses *basic* regular expressions. Add `-E` for *extended* ones, which are easier to read and closer to what you know from other languages.

The building blocks:

- `.` matches any single character
- `*` means zero or more of the previous item
- `^` anchors to the start of a line, `$` to the end
- `[abc]` matches any one of those characters; `[0-9]` matches a digit
- `+`, `?`, `|`, and `()` work as you'd expect with `-E`

```bash
# Lines starting with a date like 2026-11-12
grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}" app.log

# Either "warn" or "error", case-insensitive
grep -Ei "warn|error" app.log
```

**A common trap:** your shell can interpret special characters before `grep` sees them. Quote your patterns. Single quotes are the safest on bash and zsh, since they prevent any expansion.

## Pipes: where grep shines

`grep` really comes alive when you chain it with other commands:

```bash
# Is nginx running?
ps aux | grep nginx

# Which of my installed packages mention python?
dpkg -l | grep -i python

# Count unique IPs that hit a 404
grep " 404 " access.log | awk '{print $1}' | sort -u | wc -l
```

A classic gotcha: `ps aux | grep nginx` also matches the `grep nginx` process itself. The old trick is `grep "[n]ginx"`. The bracket makes the pattern not match its own command line.

## Fixed strings and speed

Searching for something with lots of special characters, like `1.2.3` or `foo(bar)`? Use `-F` to treat the pattern as a literal string:

```bash
grep -F "foo(bar)" main.c
```

It's faster and avoids escaping headaches.

## Modern alternatives

Tools like **ripgrep** (`rg`) and **ag** are faster on large codebases and respect `.gitignore` by default. If you search code all day, try `rg`. But `grep` is installed nearly everywhere, which makes it the one worth knowing cold, especially on servers, in containers, and in CI.

On Windows, PowerShell's equivalent is `Select-String`:

```powershell
Select-String -Path *.log -Pattern "error"
```

## A tiny cheat sheet

```bash
grep -rniE "pattern" .      # recursive, numbered, case-insensitive, extended
grep -rl "pattern" .        # filenames only
grep -v "pattern" file      # exclude matches
grep -C 2 "pattern" file    # context
grep -F "literal.text" file # no regex
```

## Wrapping up

`grep` isn't cryptic. It's a small tool that does one thing: filter lines by pattern. Learn the dozen flags above, get comfortable with a handful of regex building blocks, and quote your patterns. You'll find yourself reaching for it daily.

What's your favorite `grep` trick? Drop it in the comments.
