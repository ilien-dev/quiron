**rbd: update rbd open, create and remove image functions**

## Summary

This PR modernizes the image lifecycle API in the `rbd` package so that opening, creating and removing images follows a consistent, function-based style instead of depending on partially initialized `Image` structs.

## Changes

- **Open:** Adds `OpenImage(ioctx, name, snapName)` and `OpenImageReadOnly(ioctx, name, snapName)`, which return a ready-to-use `*Image` and an error. Callers no longer need to build an `Image` with `GetImage` and then call `Open()` with untyped variadic arguments to choose read-only mode or a snapshot.
- **Create:** Adds `CreateImage(ioctx, name, size, options)`, backed by `rbd_create4`, so features, order, stripe settings and data pool are passed through `ImageOptions` rather than through several positional `Create*` variants.
- **Remove:** Adds `RemoveImage(ioctx, name)` as a standalone function, so removing an image no longer requires an `Image` handle.
- **Deprecation:** The older `Create`, `Create2`, `Create3`, `Image.Open` and `Image.Remove` stay in place for compatibility. They are marked deprecated in their doc comments and point to the new functions.
- **Errors:** The new functions return typed `rbdError` values, consistent with the rest of the package.

## Testing

- Added unit tests for each new function. They cover read-only opens, opens at a snapshot, creating with `ImageOptions`, and removing both existing and missing images.
- Existing tests still pass against the containerized Ceph test environment (`make test-container`).

## Notes

This change is backward compatible. The deprecated functions will be removed in a later release according to the project's API stability policy.

---

I don't have access to the actual diff, so the function signatures and test details above are inferred from the title. Please adjust them to match the code before posting.
