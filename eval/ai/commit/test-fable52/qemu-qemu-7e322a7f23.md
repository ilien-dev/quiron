hw/riscv: Use load address rather than entry point for fw_dynamic next_addr

When booting with a fw_dynamic firmware such as OpenSBI, QEMU fills in
struct fw_dynamic_info and passes it to the firmware. The next_addr
field tells the firmware where to jump once it has finished its own
initialisation and is ready to hand control to the next boot stage,
normally in S-mode with the MMU disabled.

Until now next_addr has been set to the entry point returned by the
kernel loader. For flat binaries and Image files this is the address
the payload was loaded at, so the two values are the same and
everything works. For ELF payloads it is e_entry taken from the ELF
header, which is not necessarily an address the firmware can jump to.
A Linux vmlinux is the obvious example: its entry point is a kernel
virtual address, while the segments are placed in guest RAM according
to their physical addresses. The firmware then jumps to an address
that is not backed by anything while translation is off, and the guest
takes a fault immediately after leaving M-mode, with no output to
explain why.

The firmware needs the physical address at which the image actually
sits in memory, so record the lowest load address of the image when
the kernel is loaded and use that for next_addr instead of the ELF
entry point. This matches what the fw_dynamic interface expects from
the previous stage, and what a real bootloader would do when starting
the same image.

Flat binaries, Image files and ELF payloads whose entry point equals
their load address are unaffected, because both values are identical
in those cases. The entry point is still used on paths that do not go
through fw_dynamic, such as when no firmware is loaded and the reset
vector jumps straight to the kernel.
