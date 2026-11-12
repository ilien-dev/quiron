This change optimizes runtime binding for selectors in `@ngxs/store`, focusing on the work required to prepare selectors for evaluation against application state. The goal is to reduce binding overhead while preserving the behavior applications expect from existing selectors.

Selector composition is central to NGXS: selectors can depend on other selectors, and those dependencies need to be evaluated against the appropriate state. Preparing those relationships adds runtime work alongside the selector’s actual computation. This optimization targets that preparation so selector evaluation spends less time on binding.

The scope is the internal binding path. Public selector declarations, dependency ordering, and the values returned by selectors should remain compatible with existing usage. Applications should be able to benefit through their existing selector definitions without adopting a new API or changing how they select state.

Review should focus on the boundary between preparing a selector and executing it. In particular, any reduction in binding work must still respect the state context associated with each evaluation. Composed selectors should continue receiving the correct dependency results, and memoization should retain its existing semantics.

Validation should cover:

- Selectors declared on state classes, including selectors that consume their containing state.
- Composed selectors with multiple dependencies and nested selector chains.
- Dynamically created selectors and repeated evaluations with unchanged inputs.
- State updates that invalidate cached results and produce new selected values.
- Separate store instances to check that binding does not retain an unrelated state context.

Performance assessment should distinguish the cost of preparing bindings from the cost of running selector functions. Comparing both initial setup and repeated evaluation would help establish where the optimization has an effect.

Test execution and benchmark results are not included here; those should be recorded after verification.
