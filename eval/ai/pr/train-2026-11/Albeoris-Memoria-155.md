I don't have the branch or diff, so this is based on how borderless mode typically works in Memoria (Unity's `-popupwindow` argument plus native resolution). Adjust the specifics to match your changes.

---

**Support Borderless Fullscreen**

This PR adds a borderless fullscreen option alongside the existing windowed and exclusive fullscreen modes.

Exclusive fullscreen can cause slow or flickering alt-tabs, trouble with overlays and streaming software, and display mode switches on multi-monitor setups. Borderless fullscreen avoids all of this. The game runs in a frameless window that covers the whole monitor, so switching to other applications is instant.

**Changes**
- Added a "Borderless Fullscreen" entry to the window mode selector in the Memoria Launcher.
- When selected, the launcher starts the game with the `-popupwindow` argument and sets the resolution to the monitor's native size.
- The choice is saved with the other launcher settings and restored on the next launch.
- Existing configurations are unchanged. Users who never select the new option keep their current behavior.

**Testing**
- Checked that all three window modes start correctly on single- and dual-monitor setups.
- Confirmed that alt-tab, overlays and the in-game resolution behave as expected in borderless mode.
