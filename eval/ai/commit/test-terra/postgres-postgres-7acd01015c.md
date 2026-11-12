Adjust behavior of some env settings for the TAP tests of MSVC

Commit edc2332 made the LZ4, TAR, and GZIP_PROGRAM environment
variables available to TAP tests run through vcregress.pl. Their
default values match those used by Make builds, keeping the test
environments consistent across build systems.

However, vcregress.pl assigns those defaults after loading
buildenv.pl. Although buildenv.pl can set a command to a different
value, it cannot unset one: the subsequent default assignment
reinstates it. An empty value does not solve the problem because
the assignment uses Perl's ||= operator.

This can cause test failures when a command found in PATH is absent
or incompatible. For example, the tar supplied by MinGW may not
work for the tests that use it. Users need a way to disable use of
such a command when configuring their test environment.

Assign the defaults before loading buildenv.pl. This preserves the
existing defaults for MSVC builds while allowing buildenv.pl to
override or unset each variable. Tests that depend on a disabled
command can then be skipped rather than failing because of an
unsuitable executable.

Also document LZ4, TAR, and GZIP_PROGRAM in the section covering
TAP tests for MSVC builds.

Per discussion with Andrew Dunstan.

Discussion: https://postgr.es/m/YbGYe483803il3X7@paquier.xyz
Backpatch-through: 10
