## Unchoke solidity contracts `pre` package publication on master merge

This PR re-enables publication of the `pre` npm package for the Solidity contracts when changes merge into `master`. The publish step had been choked, so merges to `master` did not release a `pre` build of the contracts.

This change removes that restriction so the publish job runs on merge again. Consumers that depend on the latest `pre` contracts will receive updates after each merge, without a manual publish.

**Review focus:**
- Confirm the publish workflow runs only on the intended trigger (merge to `master`) and not on unrelated branches.
- Check that the package version and tag used for `pre` releases match the existing release scheme.

**Testing:** Verify the publish job in CI after merge, and confirm the `pre` package version on the registry matches the merged commit.
