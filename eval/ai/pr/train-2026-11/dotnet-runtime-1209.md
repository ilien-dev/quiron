This PR continues the refactoring of R2RDump’s ReadyToRun reader APIs to make them easier for ILSpy and other tools to consume. The goal is to let consumers work directly with ReadyToRun data while keeping presentation decisions in the application that displays it.

The existing library grew out of a command-line tool designed to produce complete text dumps. That background makes some interfaces less convenient for interactive consumers, which need to inspect individual methods and combine native code with metadata in their own views. This refactoring moves the API design toward those usage patterns and supports the ongoing integration of ReadyToRun inspection into ILSpy. [Background](https://github.com/icsharpcode/ILSpy/issues/1864)

The intended benefits are:

- Make ReadyToRun information easier to access programmatically from an external tool.
- Reduce the integration work needed to present that information within ILSpy’s existing assembly and method views.
- Clarify the boundary between reading binary data and formatting it for display.
- Provide a more reusable foundation for further improvements to ReadyToRun inspection.

These changes build on the earlier extraction of `ILCompiler.Reflection.ReadyToRun` from R2RDump. They continue the same direction: sharing the reader implementation across consumers and allowing each consumer to provide the presentation suited to its users. [Library background](https://cshung.github.io/posts/introduction-to-ilcompiler-reflection-readytorun/)
