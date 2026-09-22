# Diving into Husky and lint-staged

Last week I wrote about [ESLint](https://laurieontech.com/posts/eslint/), and this post is the follow-up. Once your team agrees on a ruleset, how do you make sure the main branch actually matches it? Relying on every developer to remember to run the linter before each commit isn't a strategy. So you automate it, and the formatting nitpicks mostly disappear from code review along the way.

## lint-staged

[lint-staged](https://www.npmjs.com/package/lint-staged) runs commands against staged files only. Staged means files that are new or modified and haven't been committed yet. It executes before a commit, and because it processes fewer files than a full lint, it's faster.

The configuration lives in `package.json`. Each key is a glob pattern, and each value is the command, or list of commands, to run on the matching files.

```json
{
  "lint-staged": {
    "*.js": ["eslint", "prettier --write"]
  }
}
```

In this example every staged JavaScript file goes through ESLint and then gets formatted by [Prettier](https://prettier.io/).

## Husky

Under the hood, lint-staged relies on [Husky](https://www.npmjs.com/package/husky) to hook into git. Git hooks are scripts that run at certain points in your git workflow, before a commit or before a push, for example. By default they live in `.git/hooks`, and that directory isn't tracked by git, so sharing hooks with the rest of your team is painful without extra tooling. Husky puts the hook definitions in your repository instead, under version control.

For years, Husky configuration was a `hooks` block in your `package.json`. Version 6 changed that implementation. Now each hook is a separate shell file, named after the hook.

To set it up:

```bash
npx husky-init && npm install
```

The initialization script makes sure your coworkers get Husky installed before they commit anything. Then you add a hook:

```bash
npx husky add .husky/pre-commit "npm test"
```

The generated file calls `husky.sh` first. You can remove that line, but I'd keep it. It's what makes the `--no-verify` bypass work when you need it.

## Putting them together

The example hook runs `npm test`. I swapped that out for `npm lint-staged`, and now every commit automatically lints and formats the files it modifies.

## What about pre-push?

This is the gotcha that tripped me up for a while. I tried running lint-staged in a pre-push hook and it found 0 files. Why? By the time you push, the files are already committed, so they aren't staged anymore. There's nothing for lint-staged to operate on.

If you want a pre-push check, you have two alternatives. You can lint everything:

```bash
eslint '*.js'
```

Or you can lint only the differences compared to main:

```bash
eslint --no-error-on-unmatched-pattern $(git diff main... --name-only --- '*.js')
```

Whether the diff approach works for you depends heavily on your project.

## Hooks aren't CI

Checks in a git hook let you fail fast, and that's great. Keep the pre-commit hook quick, though. If you have expensive checks, like a full test suite or type checking, a pre-push hook or CI is a better location for them. And hooks don't replace CI. Hooks can also be skipped with `--no-verify`. I run the checks in both places.
