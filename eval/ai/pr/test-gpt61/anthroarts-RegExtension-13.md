*Draft based on the title; repository changes were unavailable for verification.*

This PR introduces a state machine framework for managing workflow screens in RegExtension. It establishes a shared approach for representing the active screen and describing how a workflow moves between screens as users complete actions.

The framework’s purpose is to make workflow progression explicit and easier to reason about. By organizing screen behavior around states and transitions, it provides a foundation for extending workflows while keeping navigation rules understandable. This structure should also make it easier to review changes, identify missing transitions, and investigate unexpected navigation behavior.

The intended benefits are:

- A consistent model for defining workflow screens and their relationships.
- Clearer separation between screen presentation and workflow progression.
- A reusable foundation for adding steps and supporting more complex navigation.
- More focused validation of transitions and expected screen behavior.

Review should focus on whether the state model captures the required workflow paths, whether transitions produce the expected destination screens, and whether the framework is straightforward to extend.

Validation should cover initial screen selection, supported transitions, invalid transition handling, and any existing workflows integrated with the framework. Test execution and implementation details remain to be confirmed against the diff.
