# 4 Git shortcuts that define my workflow

I spend a lot of my day in the terminal, and a big chunk of that time is spent in Git. Over the years I've picked up a handful of shortcuts that I now use so often they feel like muscle memory. None of them are secret, but together they've shaped how I commit, how I switch context and how I keep my history clean.

Here are the four, plus the configuration to set them up yourself.

## 1. `git commit --amend --no-edit` (aliased to `git oops`)

You make a commit, push nothing yet, and immediately realize you forgot to stage a file. Or you left a `console.log` in, or the linter complains about a missing semicolon.

I used to make a second commit called "fix typo." Now I just run:

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

One word of caution. Amending rewrites the commit, which gives it a new hash. If you've already pushed that commit to a shared branch, amending means you'll need to force push, and anyone who pulled the old version will have a bad time. On my own feature branches I use it freely and then push with:

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

It sounds like a small thing, but I switch between two branches dozens of times a day, especially when I'm reviewing a PR in the middle of my own feature development. Not having to type out long branch names like `feature/JIRA-1234-refactor-auth-middleware` saves real time and a lot of typos.

`git checkout -` works too if you're on an older version of Git, but I've switched over to `git switch` for changing branches. Its intention is clearer than `checkout`, which does about five different things.

And while we're on branches, this creates a new branch and switches to it in one step:

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

It forces me to review my own code before I commit it. Paying attention to each individual hunk, I catch stray debug logs, commented-out code and accidental changes all the time. It's a small code review that happens before anyone else sees the code.

It also lets me split messy work into clean commits. Real work isn't linear. I'll be building a feature, notice a bug in an unrelated function, fix it, and keep going. With `git add -p` I can stage just the bug fix, commit it with a clear message, and then stage the feature work separately.

```bash
git add -p        # stage only the bug fix hunks
git commit -m "Fix off-by-one error in pagination"

git add -p        # stage the feature hunks
git commit -m "Add filter state to dashboard"
```

Reviewers love this. Future me, reading `git log` six months later, loves it even more.

## 4. `git rebase -i --autosquash` with fixup commits

This one builds on the previous tips and ties them together.

Say I've got a feature branch with a few commits:

```
a1b2c3d Add dashboard layout
d4e5f6g Add filter dropdown
h7i8j9k Wire filters to API
```

During review, someone points out a bug in the "Add filter dropdown" commit. I could make a new commit on top, but then the history has a "fix review comments" commit that carries no information for the next person reading it. So I make a fixup commit that targets the original one instead:

```bash
git add -p
git commit --fixup d4e5f6g
```

That creates a commit named `fixup! Add filter dropdown`. When I'm ready to clean up, I run:

```bash
git rebase -i --autosquash main
```

Git opens the interactive rebase with the fixup commit already in position under its target and marked as `fixup`. I save and close, and the fix gets squashed into the right place. The history ends up looking like the bug never existed.

You can make autosquash the default so you don't have to remember the flag:

```bash
git config --global rebase.autosquash true
```

If finding the commit hash is annoying, you can reference commits by message instead:

```bash
git commit --fixup ":/Add filter"
```

That `:/` syntax finds the most recent commit whose message matches the text.

## Bonus: a log that's actually readable

This one isn't part of my core four, but I use it constantly to see where I am before rebasing:

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```

Running `git lg` gives a compact, visual history of every branch. That makes the situation a lot easier to understand before I do anything destructive.

## How a feature goes for me

Here's what a typical feature looks like:

1. Start the branch with `git switch -c feature/thing`.
2. Write code, then use `git add -p` to build focused commits.
3. Something small forgotten gets fixed with `git oops`.
4. Getting pulled onto something else means `git switch main`, then `git switch -` to come back.
5. Review feedback gets handled with `git commit --fixup <sha>` and `git rebase -i --autosquash main`.
6. Push with `git push --force-with-lease` and merge.

None of these shortcuts are complicated on their own. The combination is what matters to me: they make it cheap to keep history clean, so I actually do it.

## Your turn

These are the four that stuck for me, but everyone's workflow is a little different. What Git shortcuts or aliases do you rely on every day? Drop them in the comments. I'm always looking to steal a good one.
