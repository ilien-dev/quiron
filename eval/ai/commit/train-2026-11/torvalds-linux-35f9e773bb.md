ACPI / x86: Add acpi_quirk_skip_[i2c_client|serdev]_enumeration() helpers

Some x86 devices describe I2C clients or serdev slaves in their ACPI
tables that should not be enumerated, or that are instantiated by
another mechanism such as a platform driver or a board-specific
instantiation table. Today the I2C and serdev core code handles these
cases with open-coded DMI checks, which duplicates logic and makes the
quirks harder to extend.

Add two helpers in drivers/acpi/x86/utils.c:

- acpi_quirk_skip_i2c_client_enumeration() takes the ACPI device of an
  I2C client and returns true if a quirk matches it.
- acpi_quirk_skip_serdev_enumeration() takes the controller's parent
  device and the ACPI device of the slave and returns true if
  enumeration should be skipped.

Both helpers consult the existing DMI-based quirk table, so the
matching data stays in one place.

This patch does not switch the I2C or serdev code paths over to the
helpers. That conversion follows in separate changes. Until then,
nothing calls the new functions, so there is no functional change.
