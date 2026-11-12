I couldn't see the diff for this PR. The working directory isn't a git repository, so the bracketed sections need your input. Once you fill them in, I can tighten the wording to match the actual changes.

## Summary
This PR improves three related areas of the networking layer: inventory (`inv`) announcement handling, mempool acceptance, and transaction and block validation. The goal is less redundant traffic, more predictable mempool behavior, and consistent validation across code paths.

## Motivation
[Explain the problem. For example: duplicate `inv` messages sent to peers, inconsistent mempool rejection reasons, or validation checks repeated between the mempool and block connection paths.]

## Changes
- **Inventory:** [Describe changes to how inventory items are queued, requested, and relayed.]
- **Mempool:** [Describe changes to admission rules, eviction, or rejection handling.]
- **Validation:** [Describe checks that were reordered, cached, consolidated, or made stricter, and why.]

## Testing
- [List new or updated unit and functional tests.]
- [Report `make check` and relevant `test_runner.py` results, quoting any failures.]
- [Describe manual testing, such as syncing against testnet, if performed.]

## Notes for reviewers
[Point out the most complex sections, any consensus-sensitive changes, and any behavior that differs from before.]
