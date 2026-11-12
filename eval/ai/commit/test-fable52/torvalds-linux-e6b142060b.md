mfd: intel-lpss: Fix I2C4 not being available on the Microsoft Surface Go & Go 2

Many DSDTs for Kaby Lake and Kaby Lake Refresh models contain a
_SB.PCI0.GEXP ACPI Device node describing an I2C attached PCA953x
GPIO expander.

This seems to be something which is copy and pasted from the DSDT
of some reference design, since this ACPI Device is present even on
models where no such GPIO expander is used at all, such as on the
Microsoft Surface Go & Go 2.

This ACPI Device is a problem because it contains a SystemMemory
OperationRegion which covers the MMIO for the I2C4 I2C controller. This
causes the MFD cell for the I2C4 controller to not be instantiated due
to a resource conflict, requiring the use of acpi_enforce_resources=lax
to work around this.

I have done an extensive analysis of all the ACPI tables on the
Microsoft Surface Go and the _SB.PCI0.GEXP ACPI Device's methods are
not used by any code in the ACPI tables, neither are any of them
directly called by any Linux kernel code. This is unsurprising since
running i2cdetect on the I2C4 bus shows that there is no GPIO
expander chip present on these devices at all.

This commit adds a PCI subsystem vendor:device table listing PCI devices
where it is known to be safe to ignore resource conflicts with ACPI
declared SystemMemory regions.

This makes the I2C4 bus work out of the box on the Microsoft Surface
Go & Go 2, which is necessary for the cameras on these devices to work.
