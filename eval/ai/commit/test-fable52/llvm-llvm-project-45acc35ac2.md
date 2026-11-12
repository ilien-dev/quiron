[ELF][PPC64] Implement IPLT code sequence for non-preemptible IFUNC

Non-preemptible IFUNC are placed in in.iplt (.glink on EM_PPC64). If
there is a non-GOT non-PLT relocation, for pointer equality, we change
the type of the symbol from STT_GNU_IFUNC to STT_FUNC and bind it to
the .glink entry.

On EM_386, EM_X86_64, EM_ARM, and EM_AARCH64, the PLT code sequence
loads the address from its associated .got.plt slot. An IPLT also has
an associated .got.plt slot and can use the same code sequence.

On EM_PPC64, the PLT code sequence is actually a `bl` instruction in
.glink. It jumps to `__glink_PLTresolve` (the PLT header), which
computes the index of the .plt slot (relocated by R_PPC64_JMP_SLOT)
and calls the dynamic loader to perform lazy binding.

An IPLT does not have an associated R_PPC64_JMP_SLOT, so we cannot use
`bl` in .iplt. The slot is relocated by R_PPC64_IRELATIVE, which is
resolved eagerly at startup, and `__glink_PLTresolve` knows nothing
about it. Branching to the PLT header from an IPLT entry computes a
bogus index and crashes at runtime as soon as the address of the
IFUNC is taken and called through the canonical PLT entry.

Instead, emit a code sequence similar to the one used by
PPC64PltCallStub::writeTo(), which loads the resolved address directly
from the .plt slot:

  addis r11, r2, off@ha
  ld    r12, off@l(r11)
  mtctr r12
  bctr

Unlike a call stub, the r2 save is omitted: the entry is reached as the
target of an indirect call or a call stub, and the caller is already
responsible for saving and restoring the TOC pointer.

To make this work, add a separate ipltEntrySize to the target
description (16 bytes on PPC64; pltEntrySize elsewhere), add a
writeIplt() target hook which defaults to writePlt(), and let
IpltSection use them for its size, symbol addresses and contents.
