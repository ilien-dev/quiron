# Git Rebase Explained Simply

If you've used Git for a while, you've probably heard someone say "just rebase it" and nodded along while quietly hoping nobody asked a follow-up question. Rebase has a reputation for being scary, mysterious, and capable of destroying your work. It doesn't have to be any of those things.

In this post, I'll explain what rebase actually does, how it differs from merge, when to use it, and the one rule you should never break.

## The Problem Rebase Solves

Imagine you create a feature branch from `main` on Monday. You spend a few days building your feature, making commits along the way. Meanwhile, your teammates have been busy too, and `main` has moved forward with several new commits.

Your history now looks something like this:

```
          A---B---C  feature
         /
    D---E---F---G  main
```

Your branch started from commit `E`, but `main` is now at `G`. Before you can integrate your work, you need to deal with the fact that the two branches have diverged.

You have two main options: **merge** or **rebase**.

## Option 1: Merge

Merging takes the two branches and ties them together with a new "merge commit":

```bash
git checkout feature
git merge main
```

The result:

```
          A---B---C---M  feature
         /           /
    D---E---F---G----  main
```

Commit `M` is the merge commit. It has two parents and records the moment the branches came together.

Merge is safe and honest. It preserves exactly what happened. The downside is that on a busy project, your history can fill up with merge commits and start to look like a tangled subway map.

## Option 2: Rebase

Rebasing takes a different approach. Instead of tying the branches together, it **picks up your commits and replays them on top of the latest `main`**:

```bash
git checkout feature
git rebase main
```

The result:

```
                  A'--B'--C'  feature
                 /
    D---E---F---G  main
```

Notice a few things:

1. There's no merge commit.
2. Your commits now appear to start from `G`, as if you'd created your branch today.
3. The commits are labeled `A'`, `B'`, and `C'`, not `A`, `B`, and `C`.

That last point is the most important thing to understand about rebase.

## Rebase Rewrites History

When Git replays your commits, it doesn't move the originals. It creates **brand-new commits** with the same changes but different parents. Since a commit's ID (its hash) depends on its parent, every rebased commit gets a new hash.

A helpful mental model: rebase is like saying, "Let me pretend I started my work from the latest version of `main`." Git takes each of your changes, one at a time, and reapplies them on the new starting point.

The original commits `A`, `B`, and `C` still exist for a while (you can find them with `git reflog`), but your branch no longer points to them.

## Handling Conflicts During a Rebase

Because rebase replays commits one by one, you might hit a conflict partway through. When that happens, Git pauses and tells you which files need attention.

The workflow looks like this:

```bash
# Git stops with a conflict
# 1. Open the conflicting files and fix them
# 2. Stage the resolved files
git add path/to/file

# 3. Continue the rebase
git rebase --continue
```

If things get messy and you want to bail out completely:

```bash
git rebase --abort
```

This returns your branch to exactly how it was before you started. It's a great safety net, so don't be afraid to use it.

One difference from merging: with rebase, you might resolve conflicts multiple times, once per commit that touches the conflicting code. With merge, you resolve them all at once. This is one reason some people prefer merging for long-lived branches.

## Interactive Rebase: Cleaning Up Your Commits

Rebase has a second superpower: **interactive mode**. It lets you edit, combine, reorder, or delete commits before sharing them.

```bash
git rebase -i HEAD~3
```

This opens an editor showing your last three commits:

```
pick a1b2c3d Add login form
pick e4f5g6h Fix typo
pick i7j8k9l Add validation to login form
```

You can change `pick` to other commands:

- `squash` (or `s`): combine this commit into the previous one
- `reword` (or `r`): change the commit message
- `edit` (or `e`): pause to amend the commit
- `drop` (or `d`): remove the commit entirely

For example, to fold that typo fix into the first commit:

```
pick a1b2c3d Add login form
squash e4f5g6h Fix typo
pick i7j8k9l Add validation to login form
```

Save and close, and Git combines them. Your reviewers now see two clean, meaningful commits instead of three, one of which was just "oops."

Interactive rebase is fantastic for tidying up a branch before opening a pull request.

## The Golden Rule of Rebasing

Here's the rule that keeps you out of trouble:

> **Never rebase commits that other people are working on.**

Remember, rebase creates new commits and abandons the old ones. If you've already pushed your branch and a teammate has based work on it, rebasing pulls the rug out from under them. Their history and yours no longer match, and untangling it is painful.

In practice:

- ✅ Rebase your own local branches freely.
- ✅ Rebase a feature branch that only you are using, even if it's pushed.
- ❌ Don't rebase `main`, `develop`, or any shared branch.

If you rebase a branch you've already pushed, you'll need to force-push. Use the safer version:

```bash
git push --force-with-lease
```

Unlike plain `--force`, this refuses to overwrite the remote if someone else has pushed changes you haven't seen yet.

## So, Merge or Rebase?

There's no universally right answer, and teams have strong opinions. Here's a simple guideline:

- **Use rebase** to keep your personal feature branch up to date with `main` and to clean up your commits before review.
- **Use merge** when integrating a finished feature into a shared branch, or when you want to preserve the exact history of how work came together.

Many teams combine both: rebase locally to stay current and tidy, then merge (or squash-merge) the pull request into `main`.

## A Quick Cheat Sheet

```bash
git rebase main              # Replay current branch on top of main
git rebase -i HEAD~N         # Interactively edit the last N commits
git rebase --continue        # Continue after resolving a conflict
git rebase --abort           # Cancel and return to the original state
git reflog                   # Find "lost" commits if something goes wrong
git push --force-with-lease  # Safely push a rebased branch
```

## Wrapping Up

Rebase isn't magic, and it isn't dangerous once you understand what it's doing. It takes your commits and replays them somewhere new, creating fresh copies along the way. That gives you a cleaner, linear history and the ability to polish your work before sharing it.

Just remember the golden rule: don't rewrite history other people depend on. Follow that, keep `git rebase --abort` and `git reflog` in your back pocket, and you'll be rebasing with confidence in no time.

Happy coding! 🚀
