# sic

**sic** is a tool to perform Sequential Import Chaining: a way to organize imports as an ordered sequence of steps, where each step can depend on the results of the steps before it.

Import workflows often start simply. One source is loaded, transformed, and made available to the rest of an application. Over time, that process can grow to include multiple sources, dependent transformations, and checks that must happen in a particular order. When those relationships are scattered across scripts or manual procedures, it becomes harder to understand what runs, why it runs, and what should happen when a step fails.

sic gives that sequence a name and a structure. It is intended for workflows where order matters and where the output of one import forms the input or prerequisite for the next.

## The idea

A sequential import chain consists of a series of stages. Each stage has a defined responsibility, and the chain progresses through those stages in order.

For example, a data preparation workflow might:

1. Import a list of accounts.
2. Import transactions associated with those accounts.
3. Enrich the transactions with reference data.
4. Validate the combined result.
5. Make the result available to a downstream process.

The second step depends on the first: transactions need accounts to refer to. Later steps depend on the data assembled earlier. Representing those dependencies as a chain makes the intended order easier to see and maintain.

A chain can be short or long. The useful boundary is not the number of steps, but whether each step has a clear purpose and a meaningful relationship to the steps around it.

## Why use sequential import chaining?

A chain helps describe a workflow in terms of **dependencies and order**. Instead of treating a collection of imports as unrelated operations, it makes the progression explicit.

This approach can help teams:

- Understand which import happens first and which work depends on it.
- Break a large import process into smaller, focused stages.
- Identify the point at which a workflow stopped or produced an unexpected result.
- Review changes to the sequence without reconstructing the process from several scripts.
- Explain the workflow to new contributors and downstream consumers.

Sequential execution is useful when later work requires earlier results. It may be less suitable when imports are independent and can safely run in parallel. Choose a structure that reflects the actual dependencies in your workflow.

## Concepts

### Import

An **import** brings information or resources into a workflow from a source. Depending on the project using sic, a source might be a file, a service, a database, or another system.

Each import should have a clear expectation about what it receives and what it produces. Those expectations make it easier to connect the import to the next stage.

### Stage

A **stage** is one step in the chain. It may perform an import, prepare a result for another import, or check that a prerequisite has been met.

Keep stages focused where practical. A stage that performs one understandable task is easier to inspect and change than one that combines many unrelated operations.

### Chain

A **chain** is an ordered collection of stages. The order communicates the dependencies between them: earlier stages establish the conditions or results needed by later ones.

When designing a chain, consider what each stage requires, what it produces, and whether the next stage can proceed if that result is missing or invalid.

### Result

A **result** is the information or state produced by a stage. The shape of a result depends on the workflow. It might be imported records, a prepared resource, or an indication that a prerequisite has been satisfied.

Document the expectations between stages, especially where one stage relies on a particular field, format, or state created by another.

## Designing a chain

Start by listing the imports and operations your workflow already performs. Put them in the order required by their dependencies, then group related work into stages with clear names.

For each stage, ask:

- What must be available before this stage starts?
- What source or input does it use?
- What does it produce for the next stage?
- How can someone tell whether its result is valid?
- What should happen if the stage cannot complete?

These questions help expose hidden assumptions. For example, an import may appear independent until you discover that it relies on identifiers created by an earlier import. Making that relationship explicit helps prevent accidental reordering.

Consider also how the chain will be run again. Some imports can safely be repeated; others may create duplicates or depend on changing external data. The appropriate behavior depends on the sources and destinations involved, so document any requirements for retries, cleanup, or partial results alongside the workflow.

## Handling failures

Sequential workflows make the location of a failure meaningful. If a required stage fails, later stages may lack the information they need to produce a valid result.

Plan for failures at the boundaries between stages. Record enough context to identify the affected input and stage, and decide how a run should be investigated or resumed. Avoid assuming that a partially completed import has left every destination unchanged.

For workflows involving external systems, account for unavailable sources, invalid records, and changes in source formats. Clear stage responsibilities make those problems easier to isolate.

## Project status and usage

This README describes the purpose and general model of sic. Installation instructions, supported environments, configuration, commands, and examples should be added here once they are confirmed for the project.

A useful usage section should show how to define a small chain, run it, inspect its result, and understand a failure. It should also state any prerequisites and explain how inputs and outputs pass between stages.

## Contributing

Contributions can improve sic’s documentation, examples, and implementation. Before proposing a change, consider how it affects the clarity of a chain and the expectations between its stages.

When reporting an issue, include the relevant environment, the sequence you attempted, the behavior you expected, and what happened instead. Remove credentials and sensitive data from logs or examples before sharing them.

When submitting a change, describe the problem it addresses and how you verified the result. Focused examples are especially helpful for explaining ordering, dependencies, and failure behavior.

## License

Add the project’s license and a link to its license file here once they are established.

---

This is a conceptual draft: I couldn’t inspect or write to the workspace because the environment rejected the filesystem command. The installation and usage details are therefore intentionally left for the project’s actual implementation.
