cryptsetup: Fix crypto device missing issue after bootup

Fix an issue where a crypto device is missing after the system has
finished booting. The expected behavior is for a device configured for
activation during boot to remain available when users and services need
to access it.

Ensure that boot-time cryptsetup handling preserves the expected device
availability through completion of startup. A successful boot should leave
the configured crypto device accessible, so subsequent consumers can use
it without requiring the administrator to activate it manually.

This addresses the case where startup completes but the resulting device
state does not match the configured setup. Keeping the device available
after boot allows later access to proceed as expected and avoids manual
recovery solely to restore the mapping.

The resulting behavior aligns boot-time activation with the expectation
that configured crypto devices remain usable once the system is running.
