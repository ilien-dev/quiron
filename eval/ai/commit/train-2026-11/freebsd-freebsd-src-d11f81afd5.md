qcom_tcsr: add initial top control and status register (TCSR) support

Introduce initial support for the Qualcomm Top Control and Status
Register block. TCSR provides system configuration controls used by
on-chip peripherals, including interface selection and operating-mode
settings that must be established during platform initialization.

Add a dedicated qcom_tcsr driver and integrate it into the Qualcomm
platform build configuration. This gives TCSR initialization its own
place in the device framework and provides a foundation for bringing
up peripherals that depend on these shared configuration registers.

The driver forms part of the platform support needed for Qualcomm
IPQ4018/IPQ4019 systems. Keeping this configuration in a dedicated
driver makes the relationship between platform setup and peripheral
operation easier to follow, while allowing support for additional
TCSR settings to be developed in the same location.

Limit this change to initial TCSR support; further peripheral support
can build on this platform initialization.

[Related FreeBSD platform integration](https://lists.freebsd.org/archives/dev-commits-src-all/2025-February/052108.html)
