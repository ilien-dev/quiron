# Diving into Husky and Lint-staged

Every team has the same story. Someone pushes a commit with a stray `console.log`, a failing formatter check, or a type error, and CI turns red five minutes later. The fix is a tiny follow-up commit, and the history gets noisier.

The best time to catch these problems is before the commit exists. That is what **Husky** and **lint-staged** are for. Together they run your linters and formatters on the files you are about to commit, and nothing else.

## What each tool does

**Git hooks** are scripts Git runs at certain points in its workflow, such as `pre-commit`, `commit-msg`, and `pre-push`. They live in `.git/hooks`, which isn't version-controlled, so sharing them with a team is awkward.

**Husky** solves that. It points Git at a versioned `.husky/` directory, so everyone who installs your dependencies gets the same hooks.

**lint-staged** solves a different problem. Running ESLint across an entire codebase on every commit is slow and punishing. lint-staged passes only the *staged* files to your commands, so the check takes seconds, even in a large repo.

## Setting it up

Install both as dev dependencies:

```bash
npm install --save-dev husky lint-staged
```

Then initialize Husky (this is the v9 flow):

```bash
npx husky init
```

This does two things. It adds a `prepare` script to your `package.json`, so hooks are installed automatically after `npm install`, and it creates a sample `.husky/pre-commit` file.

Open `.husky/pre-commit` and replace its contents with:

```bash
npx lint-staged
```

That is the whole hook. Husky v9 hook files are plain shell scripts, with no wrapper boilerplate.

## Configuring lint-staged

Add a `lint-staged` key to `package.json`:

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,css}": "prettier --write"
  }
}
```

Each key is a glob, and each value is one or more commands. lint-staged appends the matching staged file paths to each command, runs them in order, and re-stages any changes the tools made. So `eslint --fix` and `prettier --write` can rewrite a file and the fixed version ends up in your commit.

Try it: introduce some bad formatting, `git add` the file, and commit. You will see lint-staged print its tasks, and your commit will contain the cleaned-up code. If ESLint finds an error it can't fix, the commit is aborted and you get the output.

## Going beyond pre-commit

Husky supports every Git hook. Two are especially useful.

**commit-msg** pairs well with [commitlint](https://commitlint.js.org) to enforce conventional commits:

```bash
# .husky/commit-msg
npx --no -- commitlint --edit "$1"
```

**pre-push** is a good place for slower checks that would be annoying on every commit:

```bash
# .husky/pre-push
npm run typecheck && npm test
```

A useful rule of thumb: keep `pre-commit` under a few seconds, and push heavier work to `pre-push` or CI.

## A note on type checking

A common gotcha is running `tsc` through lint-staged. If you configure `"*.ts": "tsc"`, lint-staged appends file paths, and `tsc` then ignores your `tsconfig.json`. The workaround is to use a function config, which lets you control the command:

```js
// lint-staged.config.js
export default {
  "*.{ts,tsx}": () => "tsc --noEmit",
  "*.{js,ts,tsx}": "eslint --fix",
};
```

A function that ignores its arguments runs the command once, without file paths. That is what you want for whole-project checks.

## Pitfalls and good habits

**Hooks can be bypassed.** `git commit --no-verify` skips them. That's fine as an escape hatch, but it means hooks are a convenience, not a guarantee. Always run the same checks in CI as the real gate.

**Keep CI installs working.** The `prepare` script runs on install, which can fail in environments without Git. You can guard against it by setting `HUSKY=0` in CI to skip hook installation.

**Mind monorepos.** If your `package.json` isn't at the repository root, you may need to `cd` into the right directory in your hook, or use a lint-staged config per package.

**Don't make hooks slow.** If developers start reaching for `--no-verify` every time, the hook has already failed. Measure, trim, and move expensive work later in the pipeline.

**Commit your config.** The `.husky/` directory belongs in version control. That is how the whole team gets the same behavior.

## Why it's worth the ten minutes

The payoff of this setup is subtle but real. Code reviews stop containing comments about semicolons and import order. CI failures from trivial style issues disappear. New contributors get the project's standards enforced automatically, without reading a style guide.

Husky and lint-staged are small, boring tools, and that is why they work. They sit quietly in your workflow and catch the mistakes humans are bad at noticing.

If your project doesn't have them yet, set them up today. Your future self, and your reviewers, will thank you.

*Do you use other hooks in your workflow? Share your setup in the comments.*
