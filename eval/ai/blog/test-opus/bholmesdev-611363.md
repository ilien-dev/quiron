# 4 Git Shortcuts That Define My Workflow

I spend a lot of my day in the terminal, and a big chunk of that time is spent in Git. Over the years, I've picked up a handful of shortcuts that I now use so often they feel like muscle memory. None of them are particularly secret, but together they've shaped how I work: how I commit, how I switch context, and how I keep my history clean.

Here are the four Git shortcuts that define my workflow, plus how to set them up yourself.

## 1. `git commit --amend --no-edit` (aliased to `git oops`)

We've all been there. You make a commit, push nothing yet, and immediately realize you forgot to stage a file. Or you left a `console.log` in. Or a linter complains about a missing semicolon.

The old me would make a second commit called "fix typo." The current me just runs:

```bash
git add .
git commit --amend --no-edit
```

`--amend` takes whatever is staged and folds it into the previous commit. `--no-edit` keeps the existing commit message, so you don't get dropped into your editor.

Because I use this constantly, I've aliased it:

```bash
git config --global alias.oops "commit --amend --no-edit"
```

Now it's just:

```bash
git add .
git oops
```

**A word of caution:** amending rewrites the commit, which gives it a new hash. If you've already pushed that commit to a shared branch, amending means you'll need to force push, and anyone who pulled the old version will have a bad time. On my own feature branches, though, I use this freely and then push with:

```bash
git push --force-with-lease
```

`--force-with-lease` is the safer cousin of `--force`. It refuses to overwrite the remote if someone else has pushed commits you haven't seen. I basically never use plain `--force` anymore.

## 2. `git switch -` (the "go back" button)

If you've used `cd -` in your shell to jump back to the previous directory, this will feel familiar. `git switch -` checks out whatever branch you were on before.

My typical flow looks like this:

```bash
# Working on my feature
git switch feature/new-dashboard

# A bug report comes in, so I hop to main
git switch main
git pull

# Take a look, maybe start a hotfix branch...

# Then hop right back
git switch -
```

It sounds like a small thing, but I switch between two branches dozens of times a day, especially when reviewing a PR while working on my own stuff. Not having to type out long branch names like `feature/JIRA-1234-refactor-auth-middleware` saves real time and a lot of typos.

`git checkout -` works too if you're on an older version of Git, but I've fully switched over to `git switch` for changing branches. It's clearer about intent than `checkout`, which does about five different things.

While we're here, creating and switching to a new branch in one step is:

```bash
git switch -c my-new-branch
```

## 3. `git add -p` (staging with intention)

This is the one that changed the way I think about commits.

`git add -p` (short for `--patch`) walks you through every change in your working directory, hunk by hunk, and asks whether you want to stage it:

```
@@ -12,6 +12,9 @@ export function Dashboard() {
   const data = useData();
+  const [filter, setFilter] = useState('all');
+
+  console.log('data', data);
   return (
Stage this hunk [y,n,q,a,d,s,e,?]?
```

The options I use most:

- `y`: stage this hunk
- `n`: skip it
- `s`: split it into smaller hunks
- `e`: manually edit the hunk
- `q`: quit

This does two things for me.

First, it forces me to **review my own code before committing it**. I catch stray debug logs, commented-out code, and accidental changes all the time with this. It's like a mini code review that happens before anyone else sees it.

Second, it lets me **split messy work into clean commits**. Let's be honest: real work isn't linear. I'll be building a feature, notice a bug in an unrelated function, fix it, and keep going. With `git add -p`, I can stage just the bug fix, commit it with a clear message, and then stage the feature work separately.

```bash
git add -p        # stage only the bug fix hunks
git commit -m "Fix off-by-one error in pagination"

git add -p        # stage the feature hunks
git commit -m "Add filter state to dashboard"
```

Reviewers love this. Future me, reading `git log` six months later, loves it even more.

## 4. `git rebase -i --autosquash` with fixup commits

This one builds on the previous tips and ties them all together.

Say I've got a feature branch with a few commits:

```
a1b2c3d Add dashboard layout
d4e5f6g Add filter dropdown
h7i8j9k Wire filters to API
```

During review, someone points out a bug in the "Add filter dropdown" commit. I could make a new commit on top, but then the history has a "fix review comments" commit that doesn't really mean anything.

Instead, I make a **fixup commit** that targets the original:

```bash
git add -p
git commit --fixup d4e5f6g
```

That creates a commit named `fixup! Add filter dropdown`. Then, when I'm ready to clean up:

```bash
git rebase -i --autosquash main
```

Git opens the interactive rebase with the fixup commit already moved under its target and marked as `fixup`. I just save and close, and the fix gets squashed into the right place. The history ends up looking like the bug never existed.

You can make autosquash the default so you don't have to remember the flag:

```bash
git config --global rebase.autosquash true
```

If finding the commit hash is annoying, you can reference commits by message instead:

```bash
git commit --fixup ":/Add filter"
```

That `:/` syntax finds the most recent commit whose message matches the text.

## Bonus: A Log That's Actually Readable

This one isn't quite part of my core four, but I use it constantly to see where I am before rebasing:

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```

Running `git lg` gives a compact, visual history of every branch, which makes it much easier to understand what's going on before doing anything destructive.

## Putting It All Together

Here's what a typical feature looks like for me:

1. `git switch -c feature/thing` to start the branch.
2. Write code, then `git add -p` to build focused commits.
3. Notice I forgot something small? `git oops`.
4. Get pulled onto something else? `git switch main`, then `git switch -` to come back.
5. Review feedback comes in? `git commit --fixup <sha>` and `git rebase -i --autosquash main`.
6. `git push --force-with-lease` and merge.

None of these shortcuts are complicated on their own. The value comes from using them together: they make it cheap to keep history clean, so I actually do it.

## Your Turn

These are the four that stuck for me, but everyone's workflow is a little different. What Git shortcuts or aliases do you rely on every day? Drop them in the comments. I'm always looking to steal a good one.
