# Git Rebase Explained Simply

If you've been using Git for a while, you've probably heard people talk about rebasing. Maybe you've heard it's dangerous. Maybe you've heard it's the only civilized way to keep history clean. Either way, it can feel mysterious.

The good news is that the core idea behind `git rebase` is actually pretty simple. Let's break it down.

## Starting With a Picture

Imagine you create a branch called `feature` off of `main`. You make a couple of commits. Meanwhile, a teammate merges some work into `main`.

Your history now looks like this:

```
          C---D  feature
         /
A---B---E---F  main
```

Your branch started at commit `B`. Since then, `main` has moved forward with `E` and `F`. Your branch doesn't have those changes.

You want your feature branch to include the latest work from `main`. You have two main options: **merge** or **rebase**.

## Option 1: Merge

If you run:

```bash
git switch feature
git merge main
```

Git creates a new **merge commit** that ties the two histories together:

```
          C---D---M  feature
         /       /
A---B---E---F----  main
```

This is totally fine. Nothing is lost, and the history accurately shows that two lines of work happened in parallel and then came together. The downside is that if you do this a lot, your history fills up with merge commits and becomes hard to read.

## Option 2: Rebase

Now let's try the same thing with rebase:

```bash
git switch feature
git rebase main
```

Instead of tying the histories together, rebase **picks up your commits and replays them on top of the latest `main`**:

```
                  C'---D'  feature
                 /
A---B---E---F  main
```

That's it. That's rebase.

Your branch now looks like you started it from `F` instead of `B`. The history is a straight line, which is easier to read and reason about.

Notice the little apostrophes: `C'` and `D'`. That's important. These are **new commits**. They contain the same changes as `C` and `D`, but because they have a different parent, they get different commit hashes. Git doesn't move your old commits; it creates new copies and points your branch at them.

## A Helpful Way to Think About It

Here's the mental model that made rebase click for me:

> Rebase means "change the base of my branch."

Your branch has a base, which is the commit it started from. Rebasing moves that starting point to somewhere else, usually the tip of `main`, and then re-applies your work on top of it.

It's as if you said: "Pretend I started this work today instead of last week."

## What About Conflicts?

Just like with a merge, rebasing can cause conflicts if your changes and the changes on `main` touch the same lines.

The difference is that rebase applies your commits **one at a time**, so you might have to resolve conflicts at each commit instead of all at once. When it happens, Git pauses and tells you:

```
CONFLICT (content): Merge conflict in app.js
```

To handle it:

1. Open the file and fix the conflict.
2. Stage the fix with `git add app.js`.
3. Continue with `git rebase --continue`.

If things get messy and you want to bail out:

```bash
git rebase --abort
```

This puts everything back exactly the way it was before you started. It's a great safety net, so don't be afraid to use it.

## Interactive Rebase: The Power Tool

Rebase has a second superpower: **interactive mode**. It lets you edit your commits before sharing them.

```bash
git rebase -i main
```

Git opens your editor with a list of your commits:

```
pick C Add login form
pick D Fix typo in login form
```

You can change `pick` to other commands:

- `squash` or `fixup` to combine a commit into the previous one
- `reword` to change a commit message
- `edit` to stop and modify a commit
- `drop` to remove a commit entirely

You can also reorder lines to reorder commits.

For example, changing `pick D` to `fixup D` would fold that typo fix into the "Add login form" commit. Your reviewers see one clean commit instead of two.

## The Golden Rule of Rebasing

Here's the one thing you really need to remember:

> **Don't rebase commits that other people are working on.**

Because rebase creates new commits with new hashes, it rewrites history. If you rebase a branch that a teammate has already pulled, their copy and your copy will no longer match. Git will think the two histories have diverged, and untangling it is painful.

In practice, this means:

- Rebasing **your own local branch** before pushing: totally safe.
- Rebasing **your own feature branch** that only you work on, even if pushed: generally fine, but you'll need to force push.
- Rebasing **a shared branch like `main`**: don't do it.

When you do need to push a rebased branch, use:

```bash
git push --force-with-lease
```

This is safer than `--force` because it refuses to overwrite the remote if someone else has pushed changes you haven't seen.

## So, Merge or Rebase?

Honestly, both are fine. Teams have different preferences. A common approach is:

- **Rebase** your feature branch on `main` to keep it up to date and tidy while you're working.
- **Merge** (or squash merge) the finished feature into `main` through a pull request.

This gives you a clean, linear history on your branch, without ever rewriting shared history.

## Wrapping Up

To sum it up:

- `git rebase` replays your commits on top of another branch.
- It creates new commits, which gives you a clean, linear history.
- Interactive rebase lets you squash, reword, reorder, and drop commits.
- Never rebase commits that others have already pulled.
- `git rebase --abort` is always there if you get stuck.

Once you get the mental model of "change the base," rebase stops being scary and becomes one of the most useful tools in your Git toolbox. Give it a try on your next feature branch!
