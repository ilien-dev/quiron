**Motivation**

`parking_lot` has a `send_guard` feature that makes its lock guards `Send`. Because Cargo unifies features across the dependency graph, any crate in a user's build can turn this on, and tokio's wrapper types in `loom/std/parking_lot.rs` silently become `Send` too. The standard library's guards are always `!Send`, so tokio's internal code can compile under one configuration and fail under another depending on unrelated dependencies. It also allows code that moves a guard across threads, or holds one across an `.await` in a `Send` future, to slip through CI when the `parking_lot` feature is enabled.

**Solution**

Add a `PhantomData<std::sync::MutexGuard<'a, T>>` marker (and the `RwLock` read/write guard equivalents) to each wrapper guard. The marker makes the guards `!Send` regardless of how `parking_lot` is configured, so they match the `std` backend. `Sync` behavior is unchanged.

The marker is zero-sized and adds no runtime cost. This is an internal change only; no public API is affected.
