cmd/link: handle grouped resource sections

Object files produced by MSVC's cvtres and by llvm-cvtres emit
resources as grouped COFF sections named ".rsrc$01" and ".rsrc$02".
The "$" suffix is a grouping convention: the linker is expected to
strip the suffix, merge sections that share a base name, and order
the contributions by suffix. The $01 section holds the resource
directory tree, and the $02 section holds the raw data that the
tree's entries reach through relocations.

Until now loadpe only recognized sections named exactly ".rsrc". A
.syso file using grouped sections was either skipped or had its
relocations resolved against the wrong section, producing a resource
directory whose data offsets pointed at garbage. Users saw
executables with missing or corrupt manifests and icons, and the
linker gave no diagnostic.

Teach the loader to match section names by their base name up to the
first "$" and to collect every matching section in an object file.
The sections are concatenated in lexical order of their suffix into
a single .rsrc symbol. Each section's starting offset is recorded so
that relocations and symbol values inside it are adjusted by the
correct amount. Alignment padding between contributions is
preserved, so data entries stay 4-byte aligned as the PE format
requires.

Objects that use a plain ".rsrc" section take the same path with a
single contribution, so their output is unchanged.

Add a test that builds a .syso containing both grouped sections,
links it into an executable, and checks that the resulting resource
directory resolves to the expected data.
