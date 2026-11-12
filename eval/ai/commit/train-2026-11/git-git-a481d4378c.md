sparse-checkout: fix segfault on malformed patterns

Feeding sparse-checkout a pattern that the parser cannot handle could
crash Git with a segmentation fault. The parser assumed that every line
it read would yield a usable pattern entry, but malformed input, such as
an unterminated escape or a pattern that is empty after trimming,
produced an entry with unset fields. A later stage then dereferenced
that entry while matching paths.

Check each parsed pattern before it is added to the pattern list.
Patterns that cannot be interpreted are now rejected with an error
message naming the offending line, and the command exits with a nonzero
status instead of crashing. The check runs during both initial parsing
and later updates, so the same malformed input cannot reach the matcher
through either path.

Valid patterns, including negations, directory-only patterns, and
cone-mode paths, are parsed exactly as before, so existing sparse
checkouts keep working. No change is made to the matching logic itself.
Callers that already handle errors from the parser see no difference in
their interface. Only the error path is new.

A regression test feeds several malformed patterns to
`git sparse-checkout set` and checks that each one fails with an error
rather than a signal. Under ASan, the original code reproduces the crash
reliably; the fixed code does not.
