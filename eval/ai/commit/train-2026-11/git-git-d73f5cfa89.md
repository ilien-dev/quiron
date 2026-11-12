chainlint.sed: stop splitting "(..." into separate lines "(" and "..."

When a subshell begins with a command on the same line as its opening
parenthesis, chainlint.sed currently separates the parenthesis from
the command. This simplifies processing with sed: the command can be
recognized by the same expressions used for commands appearing on
their own lines, without maintaining another set of expressions for
commands immediately following a subshell opener.

Although this rewriting preserves shell behavior, it makes the
diagnostic output less faithful to the input. Test authors gain
nothing from seeing an extra line containing only an opening
parenthesis, and the unexpected formatting can make the linter look
as though it has damaged the code. The corresponding expected output
also exposes an internal parsing choice, making the self-tests less
convenient to reuse with a future implementation.

Keep the opening parenthesis and its following command together.
During processing, temporarily replace the opening parenthesis with
a caret sentinel and handle the command as though a standalone
subshell opener had already been consumed. Teach the relevant
statement recognizers to accept the sentinel, and restore the
parenthesis when emitting output. This also prevents the opening
parenthesis from being mistaken for another nested subshell while
the line is being examined.

The revised processing still produces an extra blank line immediately
before the preserved subshell-opening line. Eliminating that artifact
would complicate the sed script without improving its ability to
detect broken command chains.

Instead, adjust the check-chainlint target to disregard blank lines
when comparing actual and expected output, and update the affected
expectation files to retain cuddled subshell openers.

This comparison remains appropriate for the tests: their purpose is
to check placement of the ?!AMP?! diagnostics, and blank-line fidelity
is incidental. Moreover, chainlint.sed already discards blank lines
inside subshells so that its end-of-subshell check examines the last
statement rather than an empty trailing line. Ignoring blank lines
therefore accommodates existing output behavior while keeping the
tests focused on useful diagnostics. The expected files can now
describe the annotated shell statements without recording this
particular line-splitting convention.
