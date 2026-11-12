# Git Rebase Explained Simply

Most developers learn `git merge` on day one and then spend months avoiding `git rebase`, because someone once told them it "rewrites history" and can destroy their work. That warning is half true and mostly unhelpful. Rebase is a simple idea, and once you see what it does, the fear goes away.

## The problem rebase solves

You create a branch called `feature` from `main` and make two commits. Meanwhile, your teammates push two commits to `main`. The history now looks like this:

```
A---B---E---F   main
     \
      C---D     feature
```

Your branch started at `B`, but `main` has moved on to `F`. You want your work to include the latest changes. You have two options.

## Option one: merge

```bash
git switch feature
git merge main
```

Git creates a new merge commit that ties the two lines together:

```
A---B---E---F       main
     \       \
      C---D---M     feature
```

Nothing is rewritten, and the history records exactly what happened. The downside is that on a busy team, these merge commits pile up and the log turns into a tangle of crossing lines.

## Option two: rebase

```bash
git switch feature
git rebase main
```

Rebase takes your commits, sets them aside, moves your branch to the tip of `main`, and replays your commits one at a time on top:

```
A---B---E---F             main
             \
              C'---D'     feature
```

The name describes the result: your branch has a new base. It used to be based on `B`, and now it's based on `F`. The history is a straight line, as if you had started your work after your teammates finished theirs.

## The one detail that matters

Notice the labels changed to `C'` and `D'`. That's not decoration. A commit's ID is a hash calculated from its contents, its message, and its parent. When `C` is replayed on top of `F`, its parent changes, so it gets a new hash. `C'` contains the same change as `C`, but as far as Git is concerned it is a different commit.

So "rewriting history" means that rebase doesn't move commits; it creates new copies and abandons the originals. Everything risky about rebase follows from this fact.

## The golden rule

**Don't rebase commits that other people have based work on.**

If a teammate has pulled your branch and built on commit `C`, and you then rebase and replace `C` with `C'`, their history no longer matches yours. Git sees two different commits with the same change, and sorting that out is painful.

In practice:

- Your own feature branch that only you work on: rebase freely.
- `main`, `develop`, or any shared branch: never rebase.

## Handling conflicts

Because rebase replays commits one by one, a conflict can show up at any step. When it does, Git pauses and tells you which files are affected. The process is:

```bash
# 1. Open the files and fix the conflict markers
# 2. Stage the fixed files
git add path/to/file

# 3. Carry on with the next commit
git rebase --continue
```

If things go badly and you want out:

```bash
git rebase --abort
```

This puts your branch back exactly where it was before you started. Knowing that `--abort` exists makes rebase much less stressful, because you can always back out mid-flight.

## Pushing after a rebase

If you already pushed your branch before rebasing, a normal `git push` will be rejected, because the remote has the old commits and you have the new copies. You need to force the push, and there is a safe way to do it:

```bash
git push --force-with-lease
```

Plain `--force` overwrites whatever is on the remote. `--force-with-lease` only overwrites if the remote branch is in the state you last saw. If someone else pushed in the meantime, it refuses, and you avoid deleting their work.

## Interactive rebase: cleaning up your commits

Rebase has a second use that has nothing to do with catching up to `main`. Interactive mode lets you edit your own commits before sharing them:

```bash
git rebase -i HEAD~3
```

Git opens an editor listing your last three commits:

```
pick a1b2c3d Add login form
pick e4f5g6h Fix typo
pick i7j8k9l Add form validation
```

Change the word at the start of each line to tell Git what to do:

- `pick` keeps the commit as is.
- `reword` keeps the change but lets you edit the message.
- `squash` combines the commit with the one above it and merges the messages.
- `fixup` does the same but throws away the commit's message.
- `drop` removes the commit entirely.

You can also reorder commits by reordering the lines. To fold that typo fix into the first commit:

```
pick a1b2c3d Add login form
fixup e4f5g6h Fix typo
pick i7j8k9l Add form validation
```

Save, close, and you have two tidy commits instead of three. Reviewers see a clear story instead of "wip", "fix", and "actually fix".

## If you break something

Remember that rebase abandons the old commits rather than deleting them. Git keeps them around for a while, and the reflog records everywhere your branch has pointed:

```bash
git reflog
```

Find the entry from just before the rebase and go back to it:

```bash
git reset --hard HEAD@{5}
```

Be aware that `reset --hard` discards uncommitted changes, so commit or stash anything you care about first. With that caveat, it is very hard to permanently lose committed work with rebase.

## Merge or rebase?

They are not rivals. A common workflow uses both:

1. Rebase your feature branch onto `main` to stay up to date.
2. Use interactive rebase to tidy your commits before review.
3. Merge the finished branch into `main` through a pull request.

Rebase keeps your private work clean, and merge records when it joined the shared history.

## Summary

- Rebase replays your commits on top of another branch, giving a linear history.
- The replayed commits are new copies with new hashes.
- Only rebase branches that are yours alone.
- Use `--continue` after fixing conflicts and `--abort` to back out.
- Push rebased branches with `--force-with-lease`.
- Use `git rebase -i` to squash, reword, and reorder commits.
- The reflog is your safety net.

Try it on a throwaway repository first. After a few practice runs, rebase stops being the scary command and becomes one you use every day.
