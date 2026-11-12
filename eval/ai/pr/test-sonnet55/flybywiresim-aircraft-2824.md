## Summary of Changes

Unit conversion setup in the options code was being initialized more than once. This PR makes it run only at start up, so the unit setting (kg/lbs) is read and applied a single time when the aircraft loads, not re-initialized afterwards.

- Moved the unit conversion initialization into the start up path only.
- Removed the repeated initialization that ran outside of start up.
- No change to the available options or their default values.

## Why

Re-running the initialization after start up does unnecessary work and can overwrite values that were already set. Doing it once keeps behavior predictable and avoids unexpected resets of the selected unit.

## Screenshots (if necessary)

N/A

## References

N/A

## Additional context

No user-visible change is intended. Behavior at load should be identical to before. The only difference is that the conversion is no longer re-initialized later.

## Testing instructions

1. Load into the aircraft with the weight unit set to kg. Confirm that the EFB, MCDU, and fuel/payload displays show kg.
2. Repeat with the unit set to lbs.
3. Change the unit option while in flight and confirm the values stay consistent and nothing resets unexpectedly.
4. Restart the flight and confirm the chosen unit persists.
5. Check the console for new errors or warnings.

## How to download the PR for testing

- Open the **Checks** tab of this PR.
- Go to **Artifacts** and download the build for the aircraft variant you want to test.
- Extract it into your Community folder, replacing any existing install.

---

I wrote this without seeing the diff, so the description of what changed (kg/lbs, repeated initialization) and the testing steps are inferred from the title. Please adjust them to match the actual code and add the `Fixes #` reference if there is one.
