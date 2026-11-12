I use maybe fifteen Git commands in a normal week. Most are the ones everybody uses: `status`, `pull`, `push`, `commit`. But four of them do far more work than the rest, and each one removed a small bit of friction I used to hit dozens of times a day.

None of these are obscure. They have been in the official docs for years. I just went a long time without using them, and I suspect a lot of people are in the same spot.

## 1. `git switch -`: go back to where I was

The dash means "the branch I was on before this one", the same way `cd -` takes you to the previous directory in a shell.

```bash
git switch main
git pull
git switch -      # back on my feature branch
```

My day is full of round trips. I'm in the middle of a feature, someone asks me to look at their branch, I check it out, then I need to go back. Before I knew about the dash, I'd type the first few letters of the branch name and lean on tab completion, or run `git branch` to remind myself what I'd called it. Now I don't need to remember the name at all.

The dash works in more places than `switch`. `git checkout -` does the same thing, and `git merge -` merges the branch you just left:

```bash
git switch main
git merge -       # merge the feature branch I just came from
```

Under the hood, `-` is shorthand for `@{-1}`, and you can go further back with `@{-2}` and so on. I almost never do. One step back covers nearly every case.

## 2. `git add -p`: stage hunks, not files

`git add -p` (short for `--patch`) walks through my changes one hunk at a time and asks what to do with each:

```
(1/3) Stage this hunk [y,n,q,a,d,s,e,?]?
```

I use four of the answers constantly:

- `y` stages the hunk
- `n` skips it
- `s` splits it into smaller hunks when Git has grouped two unrelated changes together
- `q` quits, keeping what I've staged so far

This changed how I commit more than any other command. I rarely work on just one thing. While fixing a bug I'll rename a confusing variable, fix a typo in a comment, and leave a debug print in. With `git add .`, all of that lands in one commit with a message like "fix login bug and other stuff". With `-p`, I stage the bug fix and commit it, then stage the rename and commit that, and the debug print never gets staged at all.

The second benefit is one I didn't expect: it's a code review of my own work. Reading each hunk before it goes in catches the leftover `console.log`, the commented-out block, the config value I changed for local testing. I catch something this way most days.

The same flag works on other commands:

```bash
git restore -p    # discard selected hunks from the working tree
git stash -p      # stash only some of my changes
git reset -p      # unstage selected hunks
```

One caveat: `-p` only looks at tracked files. A brand new file needs a plain `git add path/to/file` first, or `git add -N path/to/file` to mark it as "intent to add" so it shows up in the patch flow.

## 3. `git commit --fixup` with autosquash: fix old commits without the puzzle

Here's the situation. I have a branch with four clean commits. A reviewer points out a mistake in the second one. The fix is two lines.

I could add a fifth commit called "address review comments", but then the history tells a story about my mistakes instead of about the change. I could do an interactive rebase and mark the commit for editing, but that's fiddly. The fixup flow is easier:

```bash
git add -p
git commit --fixup=a1b2c3d
```

That creates a commit whose message is `fixup! ` followed by the subject of the target commit. It's a marker. Later, when I'm ready to tidy up:

```bash
git rebase -i --autosquash main
```

Git opens the rebase todo list with the fixup commit already moved under its target and marked `fixup`. I save, close, and the two-line fix is folded into the commit where it belonged.

Two config lines make this smoother:

```bash
git config --global rebase.autoSquash true
git config --global alias.fixup "commit --fixup"
```

The first makes `--autosquash` the default for interactive rebases, so I can't forget it. The second lets me type `git fixup a1b2c3d`.

What I like about this is that it separates two jobs. Making the fix happens now, while the reviewer's comment is fresh, and takes ten seconds. Cleaning the history happens once, at the end, in a single rebase. I can pile up five fixups over an afternoon of review and squash them all in one pass.

This rewrites history, so the push afterwards has to be a force push. I use `git push --force-with-lease`, which refuses to overwrite the remote branch if someone else has pushed to it since I last fetched. I only do this on my own branches, never on shared ones.

## 4. `git lg`: a log I can read

Plain `git log` gives each commit six lines and no sense of how branches relate. So the first thing I set up on any new machine is this alias:

```bash
git config --global alias.lg "log --graph --oneline --decorate --all"
```

Now `git lg` prints something like:

```
* 3f2a91c (HEAD -> feature/export) Add CSV export endpoint
* 8be04d7 Extract report builder
| * c41e7aa (origin/main, main) Bump dependencies
|/
* 5d90b12 Fix timezone handling in reports
```

One commit per line, branch and tag names attached, and the graph on the left showing where things diverged. From that small picture I can tell that my branch is two commits ahead of where it forked, that `main` has moved by one commit since, and that I'll want to rebase before opening a pull request.

I run this more than any other command except `git status`. Before a rebase, to see what I'm about to move. After a rebase, to confirm it did what I meant. After a fetch, to see what changed. When I come back from lunch and can't remember what state I left things in.

It's also the quickest place to find the hash for a `--fixup`, which is why these two sit together so well.

## What they have in common

None of the four lets me do something I couldn't do before. I could always type a branch name, stage whole files, rebase by hand, and read the long log. What they change is the cost. When switching back is one character, I stop avoiding context switches. When staging is per hunk, small focused commits become the default. When fixing an old commit takes ten seconds, I stop writing "misc fixes". When the graph is one short command away, I check it before acting instead of after something goes wrong.

If you only try one, make it `git add -p`. It's the one that changed the quality of what I ship; the others mostly made me faster.

Which shortcuts carry your workflow? I'd like to hear about them in the comments.
