This PR adds `I2C_eeprom_cyclic_store<T>`, a utility class for persisting a single data structure while distributing writes across EEPROM pages. It is intended for frequently updated settings, configuration, or metrics, where repeatedly writing to a fixed address can concentrate wear and shorten the memory’s useful life.

The utility divides the configured EEPROM region into slots, each containing enough contiguous pages for the data and a version header. Each write advances to the next slot, increments the version, and wraps back to the beginning after reaching the end of the region. During initialization, the class locates the latest stored version so applications can resume reading and updating their data after a restart. This moves address rotation and version tracking into a reusable interface. See the [cyclic storage documentation](https://github.com/RobTillaart/I2C_EEPROM/blob/master/README_cyclic_store.md).

The interface provides:

- `begin(eeprom, pageSize, totalPages)` to configure storage and locate the current record.
- `format()` to reset slot headers before reusing incompatible storage.
- `read(buffer)` to retrieve the current record.
- `write(buffer)` to save the next version.
- `getMetrics(slots, writeCounter)` to report slot capacity and accumulated writes.

Pointer and reference overloads support reading and writing typed buffers. The metrics allow applications to estimate average writes per slot and assess how evenly the available storage is being used.

Data is stored as a raw binary representation, so the stored type should be a simple value-only structure. Changes to its layout, size, or architecture require reformatting the storage. Existing unrelated EEPROM contents also require formatting before use. The implementation uses a 32-bit version counter and does not support counter rollover. These constraints are documented in the [utility header](https://github.com/RobTillaart/I2C_EEPROM/blob/master/I2C_eeprom_cyclic_store.h).
