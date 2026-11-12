usb: typec: port-mapper: Convert to the component framework

The port mapper currently relies on custom code to find the USB
ports that a Type-C port is connected to, and to track their
lifetime. The matching is done by walking the device hierarchy and
comparing firmware node handles, which has to be repeated every time
a Type-C port or a USB port is registered, and it needs special
handling for whichever of the two devices happens to appear first.

The component framework exists for exactly this situation: a set of
independent devices that must all be present before the combined
functionality can be brought up. Convert the port mapper to use it.
The Type-C port and the USB ports it is connected to are registered
as component masters and components respectively, and the aggregate
device is bound only once every part is available. Likewise, the
link between them is removed when any part goes away.

This removes the open-coded matching and the ordering workarounds,
and lets the driver core handle probe deferral and unbind. No
functional change is intended for users: the same links are created
in sysfs under the same names.
