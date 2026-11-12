Here's a draft. I couldn't see the diff, so check the specifics (class names, build flags, test results) against the actual changes before posting.

---

## Android API 30+ Triage due to Loss of NetlinkSockets

### Summary

Starting with Android 11 (API level 30), apps targeting API 30 or later can no longer use `NETLINK_ROUTE` sockets. The platform's SELinux policy blocks `bind()` and related calls, so they fail with `EACCES`. OpenDDS's Linux network configuration monitoring is built on netlink, so on these Android versions it fails at startup or silently stops delivering interface and address change events. This PR triages the problem so that OpenDDS degrades gracefully on Android API 30+ instead of failing.

### Background

OpenDDS uses a netlink-based monitor on Linux to learn about network interface and address changes. This lets transports and discovery react when addresses appear or disappear, for example when Wi-Fi reconnects or the device moves between networks. Android uses the Linux kernel, so the monitor was built and enabled for Android targets. That worked until the platform removed app access to netlink route sockets.

Symptoms on affected devices:

- Failure to create or bind the netlink socket, with an error logged at startup.
- No address add/remove notifications, leaving transports and discovery with stale address information.
- Possible repeated error logging or retry behavior from the monitor.

### Changes

- Handle netlink socket creation and bind failure as an expected condition on Android rather than a hard error. The failure is logged once at an appropriate level and the monitor is disabled cleanly.
- Make sure the rest of the stack works without the monitor. Interface and address information is still obtained at startup through the existing non-netlink path, and no code assumes the monitor is running.
- Update the build configuration and documentation to state that dynamic network change detection is unavailable on Android API 30+ and what the fallback behavior is.
- Add comments pointing to the Android platform change so the limitation is easy to find later.

This is intentionally a triage fix. It restores a working baseline on current Android versions but does not provide replacement change notification. A proper replacement would use Android's `ConnectivityManager` network callbacks through JNI, which needs a larger design and is out of scope here.

### Testing

- Built for Android with API 30+ targets.
- Ran a basic publisher/subscriber on an API 30+ device or emulator and confirmed that it starts without netlink errors and that discovery and data exchange work.
- Confirmed that behavior on Linux and on Android below API 30 is unchanged, with the monitor still active there.
- Existing CI should confirm there are no regressions on other platforms.

### Known Limitations

- On Android API 30+, address changes after startup (for example Wi-Fi to cellular handoff) are not detected automatically. Applications may need to restart participants or transports to pick up new addresses.
- Follow-up work should be tracked in an issue for a `ConnectivityManager`-based monitor.

### Notes for Reviewers

Please focus on whether the failure is handled at the right layer and whether the log level is appropriate. It should be visible enough to explain the missing functionality without being noisy.
