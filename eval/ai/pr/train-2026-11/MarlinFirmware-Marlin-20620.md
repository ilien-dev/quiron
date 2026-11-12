## Description

On delta printers, navigating the UBL mesh edit screen (**Motion > Unified Bed Leveling > Edit Mesh**) could produce incorrect or unsafe nozzle moves. The map screen issued direct, unsegmented moves to each mesh point, which works on Cartesian machines but not on deltas, where straight-line moves must be segmented to follow the kinematics. Points outside the printable radius were also targeted without checking reachability, which could cause erratic carriage motion or halt the move.

This PR:

- Routes mesh edit moves through the segmented, kinematics-aware motion path on delta machines.
- Skips the move, leaving the cursor in place, when the selected mesh point lies outside the printable radius.
- Keeps Cartesian and CoreXY behavior unchanged.

## Requirements

Delta printer with `AUTO_BED_LEVELING_UBL` and an LCD controller enabled.

## Benefits

Mesh points can now be safely selected and fine-tuned from the LCD on delta printers.

## Related Issues

<!-- Link any related issues here, e.g. Fixes #XXXXX -->

---

I don't have the actual diff, so the specifics above are inferred from the title. Adjust the bullet points to match the real changes and fill in the issue link.
