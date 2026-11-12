build: auto-load ICU data from --with-icu-default-data-dir

When Node.js is configured with --with-icu-small-icu or built against
an ICU that ships its data separately, the data file is located only
through the NODE_ICU_DATA environment variable or the --icu-data-dir
runtime flag. The --with-icu-default-data-dir configure option
records a fallback path, but the value was not consistently passed
through to the compiled binary, so a build that relied on it still
started without full ICU data unless the user set the variable by
hand.

Propagate the configured directory into the build as the
NODE_ICU_DEFAULT_DATA_DIR define for every target that includes
node_i18n.cc. At startup, if neither --icu-data-dir nor NODE_ICU_DATA
is set, call u_setDataDirectory() with the default directory before
ICU is first used. Explicit user settings keep precedence, so existing
workflows behave exactly as before.

Quote and escape the path in configure.py so that directories
containing spaces or backslashes, which are common on Windows, reach
the compiler intact.

Distributors who install the ICU data outside the binary can now rely
on the configured location without wrapper scripts or environment
changes.

Refs: https://github.com/nodejs/node/issues/XXXXX
