## Summary

Some MajorBBS/Worldgroup modules ship with more than one DLL, which MBBSEmu previously couldn't load. Farwest Trivia is one of these. This PR adds support for modules with multiple DLLs.

## Changes

- Updated the module definition (`modules.json`) handling so a module can declare multiple DLLs rather than a single one.
- Module loading now iterates over every declared DLL, loading each into its own memory space and initializing it with the shared module context.
- Exported function lookups resolve against the correct DLL, so calls between a module's DLLs go to the intended target.
- Cleaned up duplicated single-DLL assumptions in the host and module setup code.
- Existing single-DLL modules behave as before, with no changes needed to their configuration.

## Testing

- Added unit tests covering loading of multi-DLL modules and resolving exports across DLLs.
- Ran existing module tests to confirm no regressions for single-DLL modules.
- Manually verified Farwest Trivia loads, starts up, and is playable from a client session.

## Notes

Farwest Trivia is the first multi-DLL module validated with this change. Other multi-DLL modules may reveal additional gaps, such as unimplemented imports, which can be handled separately.
