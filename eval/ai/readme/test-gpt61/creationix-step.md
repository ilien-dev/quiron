# step

> An async control-flow library that makes stepping through logic easy.

Asynchronous programs often begin with a simple sequence: load something, transform it, save the result. As that sequence grows, callbacks, branching conditions, and error handling can make the original intent harder to follow.

**step** helps you organize asynchronous work into clear, manageable stages. Give each stage a focused responsibility, make its dependencies explicit, and keep the overall flow easy to read.

## Why step?

Control flow should explain what your program does. You should be able to follow an operation from beginning to end without reconstructing its logic from scattered handlers.

Use step to structure workflows such as:

- Fetching data before processing and storing it.
- Validating input before performing an operation.
- Coordinating tasks that depend on earlier results.
- Breaking a long asynchronous routine into smaller pieces.
- Keeping failure handling close to the workflow it protects.

The goal is straightforward: less effort tracing execution, more attention on the logic that matters.

## Think in steps

Start by describing your workflow in plain language:

```text
Receive a request
  → Validate the input
  → Load the required data
  → Apply the requested change
  → Save the result
  → Return a response
```

Each line represents a useful boundary. A stage should accept the information it needs, perform one coherent operation, and produce a result the next stage can use.

Before turning that outline into code, identify which operations must happen in order, which failures should stop execution, and what information needs to travel between stages.

This small amount of planning makes asynchronous behavior easier to understand, review, and maintain.

## Keep workflows clear

Prefer descriptive names such as `loadAccount` or `saveChanges` over generic names such as `nextTask`. Readers should understand the purpose of a stage without opening its implementation.

Keep individual stages small enough to test independently. Separate business decisions from unrelated concerns, and avoid hiding important dependencies in shared mutable state.

Treat errors as part of the workflow. Decide where failures should propagate, where recovery makes sense, and how callers will learn that an operation did not complete.

When an operation has side effects, consider what happens if it runs again. Explicit retry and cleanup decisions help prevent surprising behavior.

## Getting started

Choose one asynchronous routine that is difficult to follow. Write down its stages, identify their inputs and outputs, and reorganize the routine around those boundaries.

Begin with a short sequence. Add branching or recovery only when the workflow requires it.

## Contributing

Bug reports, documentation improvements, and focused contributions are welcome. Describe the behavior you expected, what happened instead, and the smallest example that demonstrates the issue.
