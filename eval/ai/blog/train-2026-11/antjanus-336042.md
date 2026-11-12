# Demystifying the `find` command

If you've ever typed `find . -name "*.js"` and moved on with your life, you're using about 5% of one of the most useful tools in Unix. `find` has a reputation for cryptic syntax, but it follows a small, consistent grammar. Once you see it, the rest falls into place.

## The basic shape

```bash
find [where to look] [tests and actions]
```

You give `find` one or more starting directories, then an expression. It walks the tree and evaluates that expression for every file it encounters.

```bash
find . -name "*.md"
```

Here `.` is the starting point and `-name "*.md"` is a test. Files that pass the test get printed (printing is the default action).

Quote your patterns. Without quotes, your shell may expand `*.md` before `find` ever sees it, giving confusing results.

## Tests: filtering what you find

Tests are the heart of `find`. Combine as many as you like.

**By name** (`-iname` ignores case):
```bash
find . -iname "readme*"
```

**By type**: `f` for files, `d` for directories, `l` for symlinks:
```bash
find . -type d -name "node_modules"
```

**By size**:
```bash
find . -type f -size +100M
```

**By modification time**:
```bash
find . -type f -mtime -7     # modified in the last 7 days
find . -type f -mmin -30     # modified in the last 30 minutes
```

The `+n` / `-n` / `n` notation shows up everywhere: `+` means "more than," `-` means "less than," and a bare number means "exactly."

## Combining tests

Tests are joined with AND by default. For OR and NOT, use `-o` and `!`:

```bash
# JavaScript or TypeScript files
find . -type f \( -name "*.js" -o -name "*.ts" \)

# Everything that is NOT a markdown file
find . -type f ! -name "*.md"
```

The parentheses must be escaped (`\( ... \)`) so the shell doesn't interpret them.

## Pruning: skipping directories

Searching inside `node_modules` or `.git` is slow and noisy. Use `-prune`:

```bash
find . -name node_modules -prune -o -type f -name "*.js" -print
```

Read it as: "if it's named node_modules, skip it; otherwise, if it's a JS file, print it." Note the explicit `-print`, which is needed once you use `-o` with `-prune`.

## Actions: doing something with results

Printing is just the default. `find` can act on matches directly.

**Delete** (be careful):
```bash
find . -name "*.tmp" -delete
```

**Run a command per file** with `-exec`:
```bash
find . -name "*.log" -exec gzip {} \;
```

`{}` is replaced by the filename, and `\;` ends the command. Swap `\;` for `+` to batch many files into one invocation, which is much faster:

```bash
find . -name "*.js" -exec grep -l "TODO" {} +
```

## Handling awkward filenames

Filenames with spaces or newlines break naive pipelines like `find ... | xargs rm`. Use null separators instead:

```bash
find . -name "*.bak" -print0 | xargs -0 rm
```

Or skip `xargs` entirely with `-exec ... +`.

## Safety habits

1. **Preview first.** Run without `-delete` or `-exec rm` and read the list.
2. **Put `-delete` last.** Order matters: `find . -delete -name "*.tmp"` deletes everything.
3. **Limit depth** with `-maxdepth 2` when you don't need a full traversal.

## A few recipes worth memorizing

```bash
# Empty files and directories
find . -empty

# Files larger than 50MB, sorted by size
find . -type f -size +50M -exec ls -lh {} + | sort -k5 -h

# Files changed in the last day, excluding .git
find . -path ./.git -prune -o -type f -mtime -1 -print

# Fix permissions: directories 755, files 644
find . -type d -exec chmod 755 {} +
find . -type f -exec chmod 644 {} +
```

## Wrapping up

`find` is really three ideas: a **starting point**, **tests** that filter, and **actions** that do something. Learn the handful of tests above, remember that order matters, and always preview before you delete. After that, `find` stops being cryptic and becomes the tool you reach for first.

What's your favorite `find` one-liner? Share it in the comments.
