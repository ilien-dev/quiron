# Easily Squash, Reword, Amend, and Sort Commits with Git Rebase

If your commit history looks like a mess of "fix typo," "actually fix it," and "wip please work" commits, you're not alone. Most of us don't write perfectly clean commits as we go, and that's fine, because Git gives you a powerful tool to clean things up before you share your work: interactive rebase. In this post, I'll walk through how to use `git rebase -i` to squash, reword, amend, and reorder your commits so your history actually tells a coherent story.

## Starting an Interactive Rebase

The command that kicks everything off is:

```
git rebase -i HEAD~5
```

This starts an interactive rebase covering the last five commits. You can adjust that number to cover however many commits you want to rework, or use a branch name or commit hash instead if you want to rebase everything since you diverged from another branch:

```
git rebase -i main
```

Running this opens your default text editor with a list of commits, oldest first, each prefixed with the word `pick`:

```
pick a1b2c3d Add login form
pick e4f5g6h Fix typo in login form
pick i7j8k9l Add validation
pick l0m1n2o wip
pick p3q4r5s Actually finish validation
```

This list is the interface for everything you're about to do. Changing the word before each commit tells Git what action to take.

## Squashing Commits

Squashing combines a commit into the one before it, which is perfect for cleaning up a string of small fixup commits into a single meaningful one. Change `pick` to `squash` (or the shorthand `s`) on any commit you want folded into the commit above it:

```
pick a1b2c3d Add login form
squash e4f5g6h Fix typo in login form
pick i7j8k9l Add validation
squash l0m1n2o wip
squash p3q4r5s Actually finish validation
```

After saving and closing this file, Git will open another editor window letting you write a combined commit message for each squashed group. This is your chance to write one clean message instead of stitching together several messy ones.

## Rewording Commits

Sometimes a commit's changes are fine, but the message itself is bad. For that, use `reword` (or `r`):

```
reword a1b2c3d Add login form
```

Git will pause on this commit and open your editor so you can rewrite just the message, leaving the actual changes untouched.

## Editing Commits

If you want to stop at a specific commit to make actual code changes, not just message changes, use `edit` (or `e`):

```
edit i7j8k9l Add validation
```

The rebase will pause right after applying that commit, dropping you back at your terminal. From there you can make changes, stage them, and run:

```
git commit --amend
```

Once you're satisfied, continue the rebase with:

```
git rebase --continue
```

## Sorting Commits

Interactive rebase also lets you reorder commits, simply by changing the order of the lines in the file. Git applies commits from top to bottom, so moving a line up moves that commit earlier in history. This is useful when you realize a later commit logically belongs before an earlier one, maybe a bug fix should come before the feature that depended on discovering it.

Be careful here: if commits depend on each other, reordering can create conflicts you'll need to resolve manually as the rebase replays each commit.

## Dropping Commits Entirely

If a commit shouldn't exist at all, maybe it was an experiment that went nowhere, change `pick` to `drop` (or `d`), or simply delete the line entirely. Either approach removes that commit from history as if it never happened.

## A Word of Caution

Interactive rebase rewrites history, which means commit hashes change for every commit after the point you're rebasing from. This is completely safe on a local branch nobody else has pulled from. It becomes dangerous on a shared branch, because anyone who already has the old commits will run into conflicts and confusing divergence when they try to pull afterward. As a rule of thumb: never rebase commits that have already been pushed and shared, unless you're certain nobody else is working from them, and you communicate clearly if you do.

## Wrapping Up

Interactive rebase feels intimidating at first because you're directly manipulating history, but once you've done it a handful of times, squashing, rewording, editing, and reordering commits becomes second nature. A clean, readable commit history makes code review easier, makes `git blame` actually useful, and makes your project's history something future developers, including future you, will actually thank you for.
