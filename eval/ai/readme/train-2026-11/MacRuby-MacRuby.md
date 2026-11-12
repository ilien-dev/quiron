# MacRuby

MacRuby is an implementation of Ruby 1.9 directly on top of Mac OS X core technologies such as the Objective-C runtime and garbage collector, the LLVM compiler infrastructure and the Foundation and ICU frameworks.

The project brings Ruby’s expressive syntax and dynamic programming model to the native Mac development environment. By building on the same technologies used by Objective-C applications, MacRuby lets developers explore Ruby as a language for creating Mac software and interacting with Cocoa APIs.

## Overview

MacRuby connects Ruby programming with the Mac OS X application platform. Its architecture integrates Ruby objects, execution, and memory management with native system facilities.

This approach makes it possible to combine Ruby code with Objective-C libraries while retaining familiar Ruby concepts, including classes, modules, blocks, and exceptions. Developers can use Ruby to express application logic while drawing on the capabilities of the underlying operating system.

MacRuby targets Ruby 1.9 compatibility. Compatibility details can vary by revision, particularly where libraries depend on implementation-specific behavior or native extensions.

## Core Technologies

MacRuby builds on several major components of the Mac OS X development stack:

- **Objective-C runtime:** Provides the runtime foundation for integration with Objective-C objects and frameworks.
- **Garbage collector:** Supports automatic memory management through the platform technology used by the project.
- **LLVM:** Supplies compiler infrastructure for translating and executing Ruby code.
- **Foundation:** Provides native facilities for collections, strings, dates, files, and other common application needs.
- **ICU:** Supplies internationalization and Unicode functionality.

Together, these components form the foundation for a Ruby implementation closely integrated with the Mac platform.

## Getting Started

Before building or running MacRuby, check the documentation included with your source distribution. Required versions of Mac OS X, Xcode, LLVM, and supporting tools depend on the revision you are using.

A typical workflow is:

1. Obtain the MacRuby source code.
2. Review the build instructions and dependency requirements.
3. Install the compatible development tools.
4. Build and install MacRuby using the documented procedure.
5. Run the test suite to verify your environment.

Keep your MacRuby installation distinguishable from other Ruby installations. When running scripts or installing libraries, confirm that your shell is using the intended interpreter.

## Working with Cocoa

MacRuby is designed for interaction with native Objective-C frameworks. Cocoa development still requires familiarity with framework conventions, object relationships, application lifecycles, and platform APIs.

Start with a small example that loads a framework and interacts with a native object. Then explore larger examples involving application behavior and user interfaces. Consult the examples and API documentation supplied with your checkout for supported syntax and framework-loading conventions.

## Compatibility and Libraries

Pure Ruby libraries are a useful starting point when evaluating compatibility. Libraries with native extensions may require changes because MacRuby’s runtime architecture differs from other Ruby implementations.

Test dependencies early, especially when they rely on C APIs, threading assumptions, memory management behavior, or platform-specific features.

## Contributing

Contributions can include bug reports, documentation improvements, compatibility fixes, tests, and examples. Before submitting changes, review any contribution guidelines included in the repository.

For bug reports, provide your Mac OS X version, MacRuby revision, reproduction steps, and relevant output. Focused changes with clear explanations and regression tests are easier to review.

## License

Consult the repository’s license files for licensing terms.
