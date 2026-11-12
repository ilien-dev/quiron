I didn't have access to the diff, so this is based only on the title. Check the claims against the code before posting.

## Summary

This PR allows a single settlement submission to target multiple settlement destinations at the same time, rather than requiring one submission per target. Related settlements can now be batched into one pass, which reduces round trips and keeps them in the same submission window.

## Changes

- Extend settlement submission to accept multiple targets and dispatch them concurrently.
- Report failures per target so one failed target does not silently drop the others.
- Add tests for concurrent submission, partial failure, and the single-target path, which should behave as before.

## Reviewer notes

- Please check the ordering guarantees between targets and how nonces are handled.

If you share the diff or the list of changed files, I can make this description match the actual changes.
