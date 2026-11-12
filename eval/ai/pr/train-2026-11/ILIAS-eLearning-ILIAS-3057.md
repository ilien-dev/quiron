*Draft based on the title; implementation details and test results were not available for verification.*

This pull request introduces smoke tests for the UI component examples in ILIAS. The aim is to catch basic execution and rendering failures early, helping maintainers keep the examples useful as both documentation and a starting point for development.

Component examples demonstrate how UI elements are constructed and used. When an underlying interface, dependency, or rendering requirement changes, an example can become outdated even when the component’s individual tests still pass. Developers following that example may then encounter errors that are difficult to distinguish from mistakes in their own implementation. Exercising the examples directly provides an additional check that the documented usage remains executable.

The smoke tests focus on a simple expectation: the covered examples should run and produce their output without unexpected failures. This establishes a baseline for example health and helps expose problems such as incompatible method calls, missing setup, or exceptions encountered while constructing and rendering components. A failure should make it clear which example needs investigation, allowing contributors to reproduce the issue and determine whether the example or the underlying implementation requires a correction.

This coverage complements the existing tests by exercising components through their example usage. Unit tests remain responsible for detailed contracts and edge cases, while these smoke tests check whether the pieces used by an example continue to work together. Keeping that distinction clear makes the tests easier to understand and helps avoid assertions that are overly sensitive to incidental markup changes.

The intended benefits are:

- Earlier detection of examples that break after changes to shared UI code.
- More confidence that documented usage remains compatible with component interfaces.
- Less dependence on manually opening examples to discover basic failures.
- Clearer feedback when a change affects multiple examples or component families.
- A repeatable baseline for reviewing future changes to the examples.

The scope is deliberately limited to basic execution and rendering. Passing smoke tests does not establish that a component looks correct, meets accessibility requirements, or behaves correctly through every interaction. Those concerns still require appropriate automated checks and manual review. The value of this change is that obvious breakage can be identified before reviewers spend time evaluating those deeper aspects.

Review should pay particular attention to how examples are selected, how their required context is supplied, and how failures are reported. Examples with special prerequisites should be handled explicitly so that the suite’s coverage is understandable. Test setup should also avoid introducing dependencies between examples, since one example’s state should not determine whether another succeeds.

Validation should include running the smoke tests alongside the relevant existing UI tests. It should also confirm that a deliberately broken example produces a useful failure and that an unaffected example continues to pass independently. Any exclusions or environment requirements should be documented with enough detail for another contributor to reproduce the run.

With this coverage in place, changes to UI components can be reviewed with an additional signal: whether the covered examples still execute successfully. This helps keep example code dependable as the UI implementation evolves and gives contributors a practical way to detect regressions in documented usage.
