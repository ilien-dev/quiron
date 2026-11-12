Add implementations of POSIX mmap and munmap functions.

Add basic mmap and munmap entry points to LLVM libc for Linux, using
internal system call helpers for x86_64. Translate kernel error returns
into errno values and the failure results expected by each function.

Add the declarations, types, constants, and syscall numbers needed to
expose these interfaces through the generated headers. Update the libc
specifications and CMake rules to build the new entry points and their
dependencies. Include tests for the syscall helpers and memory-mapping
functions.

This implementation provides the minimum functionality needed for these
interfaces rather than attempting to reproduce the implementations in
other libc libraries. The syscall helpers and entry points currently
depend on Linux and x86_64 details. Leave TODOs where operating-system
and architecture abstractions would make the arrangement cleaner and
more scalable.

Developing those abstractions is outside the scope of this change.
Follow-up work can address the identified areas as support for additional
platforms and architectures is added.
