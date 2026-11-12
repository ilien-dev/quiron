block: drop tighten_restrictions

The tighten_restrictions parameter was threaded through the permission
update helpers so that callers could tell whether a graph change would
make the permissions on a node more restrictive. Only one caller ever
looked at the result, and that caller now performs the permission check
unconditionally, so the information is no longer used for anything.

Keeping the flag around has a cost. Every function on the path has an
extra argument, and each caller has to decide how to initialize it and
whether to pass NULL. The out-parameter also makes it harder to see
which permission changes are actually checked and which are only
committed, which is confusing when reading the code.

Remove the parameter from all affected functions and drop the local
variables that carried it. Callers that previously passed NULL or a
dummy bool now simply omit the argument.

No functional change intended. The permission checks are performed in
the same places and in the same order as before, and the error
reporting paths are untouched.
