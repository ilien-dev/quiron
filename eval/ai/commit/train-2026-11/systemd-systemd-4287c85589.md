meson: create new libsystemd-core.so private shared library

The code in src/core/ is currently built into a static library,
libcore.a, which is then linked into the systemd binary itself as well
as into systemd-analyze and a sizeable number of test executables. Since
this library is large, every consumer carries its own full copy of it,
which inflates both the build tree and the installed footprint. For
installed binaries this is particularly wasteful: PID1 and
systemd-analyze end up shipping two nearly identical multi-megabyte
blobs of the same code.

Let's follow the approach we already use for libsystemd-shared and turn
the core code into a private shared library, libsystemd-core-<version>.so,
installed into the same private directory under rootpkglibdir. The
version suffix ensures that a binary is never accidentally combined
with a library from a different build, which matters because we make no
ABI promises whatsoever for this library. The rpath of the consumers is
set accordingly, so the library is not visible to the dynamic linker
for anything else on the system.

The static library is still built, because the fuzzers and some tests
want to link against it statically, and because builds with
-Dlink-systemctl-shared=false and friends should keep working as
before. A new option, -Dlink-systemd-core-shared, is not added for now;
if packagers need it we can add it later.

On a typical x86-64 build with debug info stripped this saves roughly
3 MB of installed size, and noticeably reduces link times for the test
suite. Start-up time of PID1 is not measurably affected, since
libsystemd-shared is already loaded dynamically anyway and one
additional DSO is negligible.
