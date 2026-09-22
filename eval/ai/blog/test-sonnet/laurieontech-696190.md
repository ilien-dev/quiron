# Diving into Husky and Lint-staged

If you've worked on a team project of any real size, you've probably run into the problem of inconsistent code quality creeping into your codebase — a missing semicolon here, an unformatted file there, maybe even a console.log that slipped through into a commit. Git hooks are a great way to catch these issues before they ever make it into your repository, and two tools in particular make this incredibly easy to set up in a JavaScript project: Husky and lint-staged.

## What Are Git Hooks?

Git hooks are scripts that run automatically at certain points in your Git workflow — before a commit, before a push, after a merge, and so on. They live in the `.git/hooks` directory of your repository by default, but that directory isn't tracked by Git, which makes sharing hooks across a team painful without extra tooling.

That's where Husky comes in.

## What Is Husky?

Husky is a tool that makes it easy to manage Git hooks in a way that *is* version-controlled and shareable across your whole team. Instead of manually configuring hooks in the untracked `.git/hooks` folder, Husky lets you define hooks in your project configuration, so everyone who clones the repo and installs dependencies automatically gets the same hooks set up.

### Installing Husky

```bash
npm install husky --save-dev
```

Once installed, you can initialize Husky:

```bash
npx husky init
```

This creates a `.husky` directory in your project and adds a `prepare` script to your `package.json` that ensures hooks are installed whenever someone runs `npm install`.

### Adding a Hook

Let's say we want to run a script before every commit. Husky makes this simple:

```bash
echo "npm test" > .husky/pre-commit
```

Now, every time someone tries to commit, `npm test` runs first. If the tests fail, the commit is blocked.

This is powerful on its own, but running your entire test suite (or full lint check) on every single commit can get slow, especially in larger codebases. That's where lint-staged comes in.

## What Is Lint-staged?

Lint-staged is a tool that runs scripts against only the files that are staged for commit — not your entire codebase. This means instead of linting or formatting every file in your project every time you commit, you only process the handful of files you actually changed.

This makes the whole pre-commit process dramatically faster, especially as your project grows.

### Installing Lint-staged

```bash
npm install lint-staged --save-dev
```

### Configuring Lint-staged

You can configure lint-staged in your `package.json`, or in a separate `.lintstagedrc` file. Here's an example `package.json` configuration:

```json
{
  "lint-staged": {
    "*.js": "eslint --fix",
    "*.{js,css,md}": "prettier --write"
  }
}
```

This tells lint-staged to run ESLint (with auto-fix) on staged JavaScript files, and Prettier on staged JS, CSS, and Markdown files.

## Combining Husky and Lint-staged

The real magic happens when you combine the two. Instead of running your full test suite or linter on every commit, you use Husky to trigger lint-staged, which only processes the files you're actually committing.

Update your `pre-commit` hook to run lint-staged instead:

```bash
echo "npx lint-staged" > .husky/pre-commit
```

Now, every time someone commits, only the staged files get linted and formatted — automatically, consistently, and without anyone needing to remember to run the linter manually.

## Why This Setup Matters

A few reasons this combination is worth setting up on any team project:

- **Consistency** — everyone's commits get the same automated checks, regardless of their local editor setup or habits
- **Speed** — lint-staged only processes changed files, so the hook doesn't slow down your workflow as the codebase grows
- **Early feedback** — catching issues at commit time is far cheaper than catching them in code review or, worse, in production
- **Reduced review noise** — formatting nitpicks in code review basically disappear, since formatting gets automatically applied before the commit even happens

## A Few Tips

- **Don't overload your pre-commit hook.** Keep it fast. If you have expensive checks (like full test suites or type checking), consider running those on a pre-push hook instead, or in CI, so they don't slow down every single commit.
- **Auto-fix where possible.** Tools like ESLint's `--fix` and Prettier's `--write` flags let lint-staged automatically correct issues rather than just flagging them, which keeps friction low for your team.
- **Make sure hooks are actually installed.** Since Husky relies on the `prepare` script running during `npm install`, double check that new team members (and CI environments, if relevant) are actually getting hooks set up correctly.
- **Combine with commit message linting if you want extra consistency.** Tools like commitlint pair nicely with Husky if your team follows a specific commit message convention (like Conventional Commits).

## Wrapping Up

Husky and lint-staged are a small addition to your project setup, but the payoff is significant: consistent code quality enforced automatically, without relying on developers remembering to run the linter themselves or reviewers catching formatting nits in every pull request.

If your team hasn't set this up yet, it's a quick win — a few minutes of configuration that pays dividends every single day afterward.
