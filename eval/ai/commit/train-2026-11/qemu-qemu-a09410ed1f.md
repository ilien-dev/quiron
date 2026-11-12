target/ppc: Remove the software TLB model of 7450 CPUs

Remove the unused software-managed TLB implementation for the 7450
family, covering the 7441, 7445, 7450, 7451, 7455, 7457, 7447, 7447a
and 7448. The preceding changes switched its remaining users to another
MMU model, leaving no CPU dependent on this implementation.

Support originally appeared in commit 7dbe11acd8, with the model
disabled because Linux lacked handlers for its TLB miss exceptions.
Commit 8ca3f6c382 subsequently enabled it when making the remaining
PowerPC 74xx CPUs selectable, without explaining why software TLB
support was appropriate for those processors.

OpenBIOS has been unable to boot with these CPU models since at least
2011. Investigation also found no suitable TLB miss handlers in Linux
5.15, FreeBSD 13, Mac OS 9, Mac OS X or MorphOS 3.15, and no other
guest software is known to rely on this emulated facility.

The affected processors now use QEMU's hardware-managed TLB emulation,
allowing them to follow the same translation path as the 7400 family.
This removes the requirement for guests to service the unsupported
software TLB miss exceptions.

Delete the obsolete MMU model and its associated initialization,
exception handling, translation helpers and instruction support. This
completes the cleanup after disabling the facility for the 7450 family
and removing unused e600 facilities, avoiding maintenance of an
unreachable implementation with no known users.

Reference: [QEMU patch discussion](https://patchew.org/QEMU/20211130230123.781844-1-farosas%40linux.ibm.com/20211130230123.781844-4-farosas%40linux.ibm.com/).
