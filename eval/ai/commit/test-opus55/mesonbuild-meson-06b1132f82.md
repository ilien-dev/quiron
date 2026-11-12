Set RPATH for all non-system libs with absolute paths

When a target links against an external shared library that is passed
by absolute path, the resulting binary can only find that library at
runtime if its directory is in the dynamic linker's search path. For
libraries in system directories this is fine, but for libraries
installed in a custom prefix (for example /opt/foo/lib or a user's
~/.local/lib) the executable fails to start from the build directory
with "cannot open shared object file" unless LD_LIBRARY_PATH is set.

Until now we only added build RPATH entries for a narrow set of these
cases, so the behaviour depended on how the dependency was found:
some libraries got a working RPATH while others, such as those
returned by find_library() or listed with absolute paths in a
dependency's link arguments, did not.

Treat all of them the same way. For every shared library given by
absolute path, if its directory is not one of the compiler's or
linker's default system library directories, add that directory to
the build RPATH. System directories are still skipped so we don't
override the default search order or leak host paths into binaries
unnecessarily.

These entries are part of the build RPATH only and are stripped on
install as before, so installed binaries continue to use
install_rpath exclusively. This makes running tests and executables
from the build directory work consistently regardless of which
mechanism was used to locate the library.
