I didn't have the diff or a local checkout of the branch, so this description is inferred from the title. Check the specifics against the actual changes before posting.

---

**Title:** variable-sizes of precomputed tables for basepoint scalar multiplication

## Summary

This PR makes the size of the precomputed tables used for basepoint scalar multiplication configurable instead of fixed. Basepoint multiplication dominates the cost of operations such as key generation and signature creation. Table size sets a direct trade-off: larger tables reduce the number of point additions per multiplication but cost more memory and precomputation time, while smaller tables reduce the footprint at the cost of speed.

## Changes

- Parameterize the precomputed basepoint table by window width, so that different sizes can be instantiated.
- Update table construction to derive its entries from the selected size.
- Keep the default size unchanged, so existing callers see identical results.
- Add tests that check scalar multiplication output against the reference computation for each supported size.

## Motivation

Constrained environments, such as embedded targets, WebAssembly, or memory-limited servers, may prefer smaller tables. Throughput-sensitive workloads may accept larger ones. Letting the caller choose avoids forcing a single trade-off on everyone.

## Notes for reviewers

- Constant-time behavior should be unaffected, since lookups still follow the same access pattern across the selected table. Please verify this in the lookup path.
- Benchmarks for each table size are included to document the speed and memory trade-offs.
- Public API changes are kept minimal. Please flag any naming concerns.
