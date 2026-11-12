# holyjit

Generic purpose Just-In-time compiler for Rust.

holyjit explores a straightforward idea: some compilation decisions are easier to make when a program is already running. By bringing just-in-time (JIT) compilation to Rust, the project aims to let programs specialize executable code using information that becomes available at runtime.

Ahead-of-time compilation gives Rust applications a strong foundation. It produces native executables, supports predictable deployment, and enables extensive optimization before a program starts. Runtime compilation offers another opportunity: generating or refining code after the application knows more about the work it needs to perform.

holyjit is intended for experiments and applications where that additional knowledge can matter. Examples include interpreters, expression evaluators, query processors, numerical workloads, and systems that repeatedly execute operations with a stable configuration.

## Why runtime compilation?

A compiler normally has to produce code that works for every supported input. At runtime, an application may discover that particular values, types, or execution paths remain constant across many operations.

A JIT compiler can potentially use those observations to produce specialized code. Instead of repeatedly interpreting an expression or checking an unchanged configuration, an application can compile a version tailored to the situation.

That flexibility comes with costs. Compilation takes time, generated code occupies memory, and specialized implementations need clear rules about when they remain valid. The useful question is therefore not simply whether generated code runs faster, but whether its benefits outweigh the cost of producing and managing it.

holyjit provides a project context for investigating those tradeoffs in Rust.

## Potential use cases

Runtime compilation can be useful when an application performs repeated work whose structure becomes known only after startup:

- **Expression evaluation:** Compile user-defined formulas or expression trees into executable operations.
- **Language implementation:** Explore compilation strategies for interpreters and domain-specific languages.
- **Data processing:** Specialize filtering, transformation, or aggregation logic for a particular workload.
- **Numerical computation:** Investigate kernels tailored to dimensions, coefficients, or operation sequences discovered at runtime.
- **Research and education:** Study compiler design, generated code, optimization boundaries, and execution strategies.

These are motivating scenarios, rather than a promise that every workload will benefit. A small calculation executed once is unlikely to justify compilation overhead. A frequently repeated computation may offer a better opportunity.

## Getting started

Begin by reading the source tree and identifying the current entry points, examples, and build configuration. The repository’s Cargo manifests are the authoritative reference for workspace members, dependencies, feature flags, and supported targets.

For a conventional Cargo checkout, these commands provide a starting point:

```sh
cargo build
cargo test
cargo doc --open
```

Check any repository-specific toolchain or configuration files before running them. Compiler projects can depend on particular Rust versions, platform facilities, or development tools.

Start with the smallest available example. Establish how a program represents work, requests compilation, invokes generated code, and releases associated resources before attempting a larger integration.

Because APIs and implementation details can evolve, prefer examples that match the revision you are building. Avoid assuming that a snippet written for another version still describes the current interface.

## Design considerations

A useful JIT interface must make several boundaries understandable: what gets compiled, when compilation happens, how generated code is called, and how long that code remains valid.

Rust makes these questions especially important. Ownership, borrowing, lifetimes, and calling conventions remain relevant even when machine instructions are generated dynamically. An implementation must account for the relationship between executable memory and any values or references used by the generated program.

Generated code also introduces platform concerns. Instruction sets, memory permissions, executable allocation, and application binary interfaces can differ across operating systems and architectures. Support should be verified against the current implementation rather than inferred from Rust’s broader portability.

When evaluating an integration, keep compilation policy separate from application semantics. The program should define its intended behavior clearly before optimization decisions enter the picture.

## Measuring results

Measure the complete workload, including initialization and compilation. Separate cold execution from repeated execution so that startup costs and steady-state behavior are both visible.

Useful measurements include compilation latency, execution time, memory consumption, and the number of executions required to recover compilation cost. Compare against a representative baseline, such as an interpreter or an ahead-of-time implementation.

Use realistic inputs and report the environment alongside results. A benchmark is most helpful when another contributor can reproduce it and understand which part of the system changed.

## Contributing

Contributions can include bug reports, documentation improvements, examples, benchmarks, and implementation work. For a bug report, provide a minimal reproduction, the relevant revision, your Rust toolchain, and platform details.

For proposed changes, explain the problem and the resulting behavior. Include focused validation where practical, especially when modifying code generation or execution boundaries.

Keep examples small, document assumptions, and distinguish observed performance improvements from expectations. Clear evidence makes compiler changes easier to review.

## License

Consult the repository’s license files for the terms governing use, modification, and distribution. Dependency licenses may impose additional obligations.
