## Summary

Adds a new `format:watch` npm script that runs Prettier in watch mode, so files are reformatted automatically as they're saved during development.

## Motivation

Currently, formatting is done through the existing `format` script, which runs Prettier once over the codebase. When working on a change over a longer session, contributors have to re-run that command by hand to keep files formatted, or wait until a pre-commit hook or CI check flags problems. A watch-mode script makes it easy to keep formatting continuous while editing, without extra tooling or editor configuration.

## Changes

- Added `format:watch` to the `scripts` section of `package.json`.
- The script reuses the same Prettier configuration and ignore rules as the existing `format` script, so output is identical to a one-off run.

## Usage

```sh
npm run format:watch
```

Leave it running in a terminal while you work; files will be reformatted when they change.

## Notes

- This is a development convenience only. It doesn't alter library code, build output, or published artifacts.
- No changes to dependencies or to the existing `format` script.
- No tests are needed, since no runtime behavior is affected.
