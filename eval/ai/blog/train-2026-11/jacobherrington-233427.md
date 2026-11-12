We've all been there. You're deep in a feature, committing fast, and your history ends up looking like this:

```
a1b2c3d fix typo
e4f5a6b WIP
c7d8e9f add login form
1a2b3c4 oops forgot file
5d6e7f8 actually fix the thing
9a8b7c6 add login validation
```

Nobody wants to review that. The good news is that Git has a tool for turning this into a clean, readable story: **interactive rebase**. In this post we'll cover the four operations you'll use most: **squash**, **reword**, **amend**, and **reordering**.

## What Is Interactive Rebase?

A normal `git rebase` replays your commits on top of another base. The interactive version, `git rebase -i`, lets you edit that replay. You get a text file listing your commits, and you decide what happens to each one.

To rewrite the last four commits:

```bash
git rebase -i HEAD~4
```

Git opens your editor with something like this:

```
pick c7d8e9f add login form
pick 1a2b3c4 oops forgot file
pick 5d6e7f8 actually fix the thing
pick 9a8b7c6 add login validation

# Commands:
# p, pick   = use commit
# r, reword = use commit, but edit the message
# e, edit   = use commit, but stop for amending
# s, squash = meld into previous commit
# f, fixup  = like squash, but discard this commit's message
# d, drop   = remove commit
```

Note that commits are listed **oldest first**, the opposite of `git log`. You change the word at the start of each line, save, and close the editor. Git does the rest.

> **Rule of thumb:** only rewrite history that hasn't been shared. Rewriting commits others have already pulled causes pain for everyone.

## Squash: Combine Commits Into One

Squashing merges several commits into one. This is the most common cleanup, and it's perfect for folding "oops" and "WIP" commits into the real work.

Say we want `oops forgot file` and `actually fix the thing` folded into `add login form`. Edit the todo list:

```
pick c7d8e9f add login form
squash 1a2b3c4 oops forgot file
squash 5d6e7f8 actually fix the thing
pick 9a8b7c6 add login validation
```

Save and close. Git combines the three commits and opens your editor again so you can write a message for the combined commit. It pre-fills it with all three original messages, and you can trim it down to something like:

```
Add login form
```

### Squash vs. Fixup

If you don't care about the folded commit's message, use `fixup` (or `f`) instead. It works exactly like squash but silently discards the message, so no second editor prompt appears.

```
pick c7d8e9f add login form
fixup 1a2b3c4 oops forgot file
fixup 5d6e7f8 actually fix the thing
pick 9a8b7c6 add login validation
```

For tiny corrections, fixup is usually what you want.

### A Shortcut: `--autosquash`

You can even prepare fixups while you work. When you spot a mistake in an earlier commit, stage the fix and run:

```bash
git commit --fixup c7d8e9f
```

Git creates a commit named `fixup! add login form`. Later, run:

```bash
git rebase -i --autosquash HEAD~5
```

Git automatically reorders the fixup commit directly under its target and marks it as `fixup`. You just save and close. If you like this workflow, enable it permanently:

```bash
git config --global rebase.autoSquash true
```

## Reword: Fix a Commit Message

Sometimes the code is fine but the message is not. Maybe you wrote `fix stuff` and now regret it. Change `pick` to `reword` (or `r`):

```
reword c7d8e9f add login form
pick 9a8b7c6 add login validation
```

When Git reaches that commit, it opens your editor with the existing message. Rewrite it, save, and you're done. The contents of the commit are untouched; only the message (and therefore the commit hash) changes.

A good commit message has a short summary line (about 50 characters), a blank line, and then an optional body explaining *why* the change was made. Rebase is a great chance to bring old messages up to that standard before opening a pull request.

## Amend: Change the Content of a Commit

There are two situations here.

### Amending the Latest Commit

If you only need to fix the most recent commit, you don't need rebase at all:

```bash
git add forgotten-file.js
git commit --amend
```

This adds the staged changes to the last commit and lets you edit its message. To keep the message as is, add `--no-edit`:

```bash
git commit --amend --no-edit
```

### Amending an Older Commit

For older commits, use `edit` (or `e`) in the todo list:

```
pick c7d8e9f add login form
edit 1a2b3c4 add password field
pick 9a8b7c6 add login validation
```

Git replays commits up to the one marked `edit`, then pauses:

```
Stopped at 1a2b3c4... add password field
You can amend the commit now, with
  git commit --amend
Once you are satisfied with your changes, run
  git rebase --continue
```

Now you're free to change files, stage them, and amend:

```bash
# make your edits
git add .
git commit --amend --no-edit
git rebase --continue
```

You can also use this pause to split one big commit into several. Run `git reset HEAD~`, then stage and commit the pieces separately with `git add -p`, and finally `git rebase --continue`.

## Sort: Reorder Commits

Reordering is the simplest operation of all: **move the lines around**. Git replays commits top to bottom, so the order in the file is the order in your new history.

Before:

```
pick c7d8e9f add login form
pick 9a8b7c6 update README
pick 5d6e7f8 add login validation
```

After:

```
pick c7d8e9f add login form
pick 5d6e7f8 add login validation
pick 9a8b7c6 update README
```

Now the two login commits sit together, and the unrelated README change is separate. Reordering is also how you prepare commits for squashing: move a commit directly beneath its target, then change it to `squash` or `fixup`.

If the commits touch the same lines, you may hit conflicts. Resolve them as usual, then run:

```bash
git add .
git rebase --continue
```

## Dropping Commits

While you're in there, you can also delete a commit entirely by replacing `pick` with `drop` (or just deleting the line). Be careful: a dropped commit's changes are gone from the branch.

## Safety Nets

Rebase feels scary at first, but Git gives you plenty of ways out.

- **Abort mid-rebase:** `git rebase --abort` returns everything to how it was before you started.
- **Undo a finished rebase:** `git reflog` shows where your branch used to point. Find the entry from before the rebase and run `git reset --hard HEAD@{n}`, where `n` is that entry's number.
- **Back up first:** `git branch backup-before-rebase` costs nothing and gives you an instant restore point.

## Pushing Your Rewritten History

Rewritten commits have new hashes, so a regular push will be rejected if the branch already exists on the remote. Use the safer form of force push:

```bash
git push --force-with-lease
```

Unlike `--force`, this refuses to overwrite the remote if someone else has pushed commits you haven't seen. Use it only on your own feature branches, never on shared ones like `main`.

## A Quick Cheat Sheet

| Command | What it does |
|---------|--------------|
| `pick` | Keep the commit as is |
| `reword` | Keep the commit, change its message |
| `edit` | Pause to change the commit's contents |
| `squash` | Merge into the previous commit, combine messages |
| `fixup` | Merge into the previous commit, discard message |
| `drop` | Delete the commit |
| *move line* | Reorder the commit |

## Wrapping Up

Interactive rebase turns a messy trail of work-in-progress commits into a clear, reviewable history. Start small: next time you're about to open a pull request, run `git rebase -i` against your base branch, squash the noise, reword anything vague, and reorder related changes together. Your reviewers, and your future self running `git blame` six months from now, will thank you.

Happy rebasing!
