target/ppc: Fix e6500 boot

The e6500 core failed to boot correctly from reset. Guest firmware and
kernels that depend on the architected e6500 reset state did not start,
because the CPU state initialised at reset did not match what the core
expects before the first instruction is fetched from the reset vector.

Correct the reset-time initialisation for the e6500 so the core starts
in the architected boot state. This brings the register defaults for
the model in line with the e6500 reference manual and with what early
boot code assumes when it begins execution at the reset entry point.

Without this change, affected machines hang or fault early in boot,
before any useful console output appears. With it, the core reaches the
expected entry point and proceeds through normal firmware and OS
startup.

The fix is confined to the e6500 CPU definition and its reset path. No
functional change is intended for other PowerPC CPU models, and the
behaviour of existing e500 and e5500 configurations is unchanged.
