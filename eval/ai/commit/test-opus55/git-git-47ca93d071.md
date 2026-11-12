repack: make '--quiet' disable progress

When 'git repack' spawns 'git pack-objects', it decides whether to
pass '--progress' based only on whether stderr is a terminal. The
'-q'/'--quiet' option is forwarded as '-q', but because '--progress'
is also passed whenever isatty(2) is true, pack-objects still shows
progress meters. As a result, 'git repack -q' run from a terminal is
not quiet at all, which surprises users and scripts that expect the
option to silence non-error output.

Fix this by teaching repack to consider '--quiet' when deciding
whether to show progress: only pass '--progress' when stderr is a
terminal and '--quiet' was not given. Store the result in a single
'show_progress' variable so the two pieces of logic cannot drift
apart again, and pass '-q' only when progress is disabled.

Add a test in t7700 that runs 'git repack -q' under test_terminal
and checks that nothing is written to stderr, guarding against a
regression.
