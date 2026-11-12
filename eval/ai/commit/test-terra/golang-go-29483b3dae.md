test: re-enable a bunch of tests with types2

Re-enable tests that were disabled when the compiler switched to the
types2 type checker. These tests provide coverage for language rules
and compiler diagnostics that should continue to be checked as types2
becomes the standard type-checking path.

Restore the affected test directives and update expectations where
necessary to account for differences in the errors produced by types2.
The restored cases include floating-point literals and shift
expressions, alongside other tests that can now run with the new
checker.

Keeping these tests in the regular suite helps catch regressions in
both the acceptance of valid programs and the rejection of invalid
ones. It also makes differences in diagnostic behavior visible as
the compiler and its tests continue to evolve.

Some tests may still require separate work where their expectations
depend on behavior that types2 does not yet match. This change
focuses on returning the compatible cases to the suite so that their
coverage is available again.
