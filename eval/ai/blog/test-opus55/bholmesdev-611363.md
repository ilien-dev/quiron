# 4 Git shortcuts that define my workflow

I've used Git for years, and for most of that time I typed every command out in full. It worked, but it was slow, and some of the most useful Git features stayed buried because they took too many keystrokes to bother with.

That changed when I started treating my `.gitconfig` like any other piece of code I maintain. I don't have dozens of aliases. I have a handful, and four of them do most of the work. They aren't clever tricks. Each one makes a good habit cheaper than a bad one.

Here they are, what they do, and why they matter to me.

---

## 1. `git lg`: see the shape of your history

```ini
[alias]
    lg = log --graph --pretty=format:'%C(yellow)%h%C(reset) %C(auto)%d%C(reset) %s %C(dim)(%cr, %an)%C(reset)'
```

The default `git log` output is verbose. Each commit takes up five or six lines, you can't see how branches relate to each other, and you end up scrolling through text instead of understanding what happened.

`git lg` gives you one line per commit, with a graph down the left side showing where branches split and merged:

```
* a1b2c3d  (HEAD -> feature/login) Add password strength meter (2 hours ago, Sam)
* e4f5g6h  Validate email on blur (3 hours ago, Sam)
| * 9i8j7k6  (origin/main, main) Bump dependencies (5 hours ago, Alex)
|/
* l5m4n3o  Merge pull request #42 (1 day ago, Alex)
```

At a glance I can see that my branch is two commits ahead and one commit behind `main`. I can see which commit I'm on, what's been pushed, and who did what.

A few variations I use constantly:

- `git lg -10` shows just the last ten commits.
- `git lg --all` shows every branch, which helps when you've lost track of something.
- `git lg main..HEAD` shows only the commits on my branch that aren't on `main`. That's exactly what will end up in my pull request.

The last one changed how I work more than anything else on this list. Before I open a PR, I run `git lg main..HEAD` and read it like a reviewer would. If the history tells a confusing story, I fix it before anyone else has to read it. That leads to the next shortcut.

---

## 2. `git fixup`: fix the right commit, not the latest one

```ini
[alias]
    fixup = "!f() { git commit --fixup=\"$1\" && GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash \"$1~1\"; }; f"

[rebase]
    autoStash = true
```

Here's a situation everyone runs into. You've made three commits on a feature branch:

```
* c3  Add tests for login form
* c2  Add login form validation
* c1  Scaffold login page
```

Then you spot a typo in the validation code from `c2`. Most people make a fourth commit called "fix typo" and move on. Now the history has a commit that only exists to correct another commit. Reviewers have to read both, and `git blame` sends future readers to "fix typo" instead of the commit that explains the change.

With this alias you stage the fix and run:

```bash
git add src/validation.js
git fixup c2
```

Two things happen:

1. `git commit --fixup=c2` creates a commit with the message `fixup! Add login form validation`.
2. `git rebase -i --autosquash c2~1` rewrites the history from just before `c2`, and Git automatically moves the fixup commit next to `c2` and squashes it in.

Setting `GIT_SEQUENCE_EDITOR=:` skips the interactive editor, because the todo list autosquash generates is already correct. The `rebase.autoStash` setting stashes any other uncommitted changes before the rebase and restores them afterward, so you don't need a clean working tree.

The result looks like the typo was never there:

```
* c3' Add tests for login form
* c2' Add login form validation
* c1  Scaffold login page
```

A couple of caveats:

- **This rewrites history.** Only use it on commits that haven't been pushed to a shared branch, or on your own feature branch where you're prepared to force-push (see shortcut #4).
- **Conflicts can happen.** If later commits touched the same lines, the rebase will stop and ask you to resolve them, just like any other rebase.
- **On Windows**, aliases that start with `!` run through Git's bundled shell, so this works in Git Bash, PowerShell, and CMD as long as you installed Git for Windows normally.

Once fixing a past commit took one command, I stopped producing "fix typo" commits altogether. My PRs now read as a sequence of meaningful steps, and reviewers have noticed.

---

## 3. `git undo`: take back the last commit without losing anything

```ini
[alias]
    undo = reset --soft HEAD~1
```

This is the smallest alias on the list and probably the one I use most.

`git reset --soft HEAD~1` moves your branch back one commit and leaves the changes from that commit **staged**. Nothing in your working directory changes. The commit simply goes away and its contents sit in the index, ready to commit again.

I reach for it when:

- I committed too early and want to add more to the commit.
- I committed to the wrong branch. I run `git undo`, then `git switch correct-branch`, then commit again.
- I want to split one big commit into smaller ones. I run `git undo`, then `git restore --staged .`, and stage pieces with `git add -p`.
- I wrote a bad commit message and want to rethink the whole commit rather than just reword it.

Why `--soft`? It's the safe option:

| Flag      | Branch moves back | Changes staged | Working files kept |
|-----------|:-----------------:|:--------------:|:------------------:|
| `--soft`  | ✅                | ✅             | ✅                 |
| `--mixed` | ✅                | ❌             | ✅                 |
| `--hard`  | ✅                | ❌             | ❌                 |

`--hard` is the one that destroys work. I deliberately don't alias it.

And if you undo something you didn't mean to, `git reflog` has your back. Every position `HEAD` has been in is recorded there, so `git reset --soft HEAD@{1}` brings the commit straight back.

Having a reversible "undo" button makes me commit more often. I don't have to get each commit perfect, because fixing it costs almost nothing.

---

## 4. `git pf`: force-push without wrecking someone else's work

```ini
[alias]
    pf = push --force-with-lease --force-if-includes
```

Shortcuts #2 and #3 both rewrite history, and rewritten history has to be force-pushed. That's where people get nervous, with good reason.

A plain `git push --force` overwrites the remote branch with your local version, no questions asked. If a teammate pushed a commit to that branch since you last fetched, their work silently disappears.

`--force-with-lease` adds a safety check. Git only overwrites the remote branch if it's still where your local copy last saw it. If someone else pushed in the meantime, the push is rejected:

```
! [rejected]        feature/login -> feature/login (stale info)
```

At that point you fetch, look at what changed, and decide what to do. Nobody's work gets lost.

`--force-if-includes` (Git 2.30 and later) closes a subtle gap. Some editors and tools run `git fetch` in the background, which updates your view of the remote. That can make `--force-with-lease` pass even though you never actually looked at the new commits. `--force-if-includes` additionally checks that the remote's current commit appears in your local history, meaning you really did incorporate it.

Together they make force-pushing a routine, low-risk part of my workflow rather than a scary exception. I use `git pf` every time I clean up a branch before review, and I never type `--force` on its own anymore.

---

## Putting it together

Here's what a typical feature looks like for me:

```bash
git switch -c feature/login
# ...work, commit, work, commit...
git lg main..HEAD          # read my branch like a reviewer
git add -p && git fixup c2 # fold a fix into the right commit
git undo                   # reshape the last commit
git pf                     # push the cleaned-up branch safely
```

Every one of these was possible before I had aliases. The difference is that now the clean option is also the fast option, so I actually do it.

To add them, run `git config --global --edit` and paste the snippets into the file, or add them one at a time:

```bash
git config --global alias.undo "reset --soft HEAD~1"
git config --global alias.pf "push --force-with-lease --force-if-includes"
git config --global rebase.autoStash true
```

(The `lg` and `fixup` aliases contain nested quotes, so pasting them into the config file directly is easier.)

What's in your `.gitconfig`? I'd love to hear which shortcuts shape your workflow in the comments.

---

It comes to about 1,190 words. I set `published: false` in the front matter so it saves as a draft on dev.to. Change it to `true` when you're ready to publish.
