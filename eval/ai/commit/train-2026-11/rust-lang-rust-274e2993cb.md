Stablize slice::strip_prefix and strip_suffix, with SlicePattern

Stabilize `slice::strip_prefix` and `slice::strip_suffix` for Rust 1.51.0,
allowing callers to remove a matching prefix or suffix and obtain the
remaining subslice without allocation. Both methods return `None` when
the pattern does not match and require `T: PartialEq`. Empty patterns
return the original slice, while a pattern matching the entire slice
produces an empty remainder.

Introduce `SlicePattern` as the abstraction for pattern arguments, with
implementations for slices and fixed-size arrays. Use its associated
`Item` type and `as_slice` method to share the existing comparison logic.
Accept patterns through `P: SlicePattern<Item = T> + ?Sized`, supporting
both forms while leaving room for future pattern capabilities.

Keep `SlicePattern` unstable so that stabilizing these methods does not
commit to a public, extensible pattern interface. Update stability
annotations and documentation examples to make the methods available
without the `slice_strip` feature gate and demonstrate their behavior
for successful and unsuccessful matches.

[Reference: Rust slice source](https://doc.rust-lang.org/src/core/slice/mod.rs.html)
