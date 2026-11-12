## Summary

This PR reworks how WorldEdit manages the CUI (client UI) lifecycle for a session. The current behaviour is spread across platform adapters and `LocalSession`, which leaves several edge cases: stale state after reconnecting, selections not being resent, and handshakes that race with player join.

## Motivation

Users of WorldEditCUI and similar clients have reported intermittent problems:

- The selection overlay disappears after changing dimensions or respawning, and only comes back once the selection is modified.
- Reconnecting to a server can leave `hasCUISupport` set from the previous connection. The server then sends events the client never asked for, or skips sending ones it needs.
- Changing the region selector (for example `//sel poly`) does not always send a full selection refresh. The client is left rendering the old shape.
- Each platform handles the handshake slightly differently, so behaviour differs between Bukkit, Fabric, Forge and Sponge.

## Changes

- **Explicit lifecycle states.** CUI support is now tracked as a small set of states (unknown, negotiated, active) instead of a boolean plus a version integer. Transitions only happen through `LocalSession`.
- **Reset on disconnect.** CUI state is cleared when a player disconnects, so a new connection always starts a fresh handshake.
- **Resend on context change.** The full selection is dispatched again after world changes, respawns and selector changes, not only after the selection is edited.
- **Centralised handshake handling.** Platform adapters now forward the raw handshake message to common code. Version negotiation and the initial selection dispatch happen in one place.
- **Deferred dispatch.** Events sent before the handshake completes are dropped consistently instead of partially, which avoids confusing clients mid-negotiation.

## Compatibility

The wire protocol is unchanged, so existing CUI clients need no updates. Some public methods on `LocalSession` are deprecated in favour of the new state-based API. They still work and delegate to the new implementation.

## Testing

- Tested manually with WorldEditCUI on Fabric and on Bukkit/Paper:
  - joining and reconnecting
  - dimension changes and respawn
  - switching between cuboid, poly and ellipsoid selectors
- Added unit tests for the session state transitions.

---

I didn't have the actual diff, so this is written from the PR title and WorldEdit's existing CUI structure. Adjust the specific changes, deprecated methods and testing notes to match what the branch actually does.
