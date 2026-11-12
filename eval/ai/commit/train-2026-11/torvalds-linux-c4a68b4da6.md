usb: phy: ab8500-usb: Keep PHY turned on in UART mode

The AB8505 USB interface can also be used for UART communication through
a Samsung UART cable. In this configuration, the PHY must remain powered
so that the serial connection continues to work. The driver currently
handles USB host, peripheral and dedicated charger states, but does not
track UART operation. Consequently, it does not keep the PHY enabled
when the reported link status identifies a UART cable.

Add a USB_UART mode and handle both Samsung UART cable link status
values in ab8505_usb_link_status_update(). When either status is reported
while the driver is idle, record the UART mode and enable the PHY using
the existing peripheral PHY helper. Handling both status values ensures
that UART cable recognition takes the same path regardless of the PHY
enable state encoded in the link status.

Track UART operation separately from USB peripheral operation so that
keeping the physical interface active does not require treating the
serial cable as a normal USB peripheral connection. The new state also
allows the disconnect handler to release the resources acquired for UART
operation: disable the peripheral PHY and return the driver to USB_IDLE
when the cable is disconnected.

This still depends on the boot firmware to configure the PHY and pin
routing for UART use. AB8505 does not appear to generate link status
changes for UART cables, and it may be unable to identify these cables
automatically. Reliable detection of a UART cable connected after boot
may therefore require explicitly measuring the resistance on the ID pin.

For now, preserve the UART configuration established by firmware and
keep its PHY resources enabled when the corresponding cable status is
observed. This provides the power handling needed for that configuration
while leaving full UART setup and detection for a later change.
