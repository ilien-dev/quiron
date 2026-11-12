Callbacks are where most C interop code gets interesting. Passing an integer or a struct across the boundary is easy. Passing *behavior* is where undefined behavior starts to creep in. This post walks through how Rust function pointers work across FFI, and the traps worth avoiding.

## `fn` is not `extern "C" fn`

A plain Rust `fn(i32) -> i32` uses the Rust ABI, which is unstable and unspecified. C cannot call it safely. To hand a callback to C, you must declare it with the C calling convention:

```rust
extern "C" fn on_event(code: i32) -> i32 {
    println!("got event {code}");
    0
}
```

The type of that function is `extern "C" fn(i32) -> i32`, which is a distinct type from `fn(i32) -> i32`. The compiler will refuse to coerce between them, and that is a feature.

## Declaring the C side

Suppose a C library exposes:

```c
typedef int (*event_cb)(int code);
void register_callback(event_cb cb);
```

The Rust binding looks like this:

```rust
type EventCb = extern "C" fn(i32) -> i32;

extern "C" {
    fn register_callback(cb: Option<EventCb>);
}
```

Notice the `Option`. A Rust function pointer is never null, but a C function pointer often can be. Thanks to the null pointer optimization, `Option<extern "C" fn(...)>` has the same layout as a nullable C function pointer, where `None` is `NULL`. Use it whenever the C API allows null. Using a bare `extern "C" fn` for a parameter that C may pass as null is instant UB.

Calling it:

```rust
fn main() {
    unsafe { register_callback(Some(on_event)) };
}
```

(On newer editions, `extern` blocks need to be written `unsafe extern "C"`.)

## Passing context with `void*`

Plain function pointers carry no state. C libraries solve this by taking a `void *user_data` that gets handed back to the callback:

```c
typedef void (*visit_cb)(int item, void *user_data);
void visit_all(visit_cb cb, void *user_data);
```

This is the pattern that lets you smuggle a Rust closure through. The trick is a *trampoline*, a generic `extern "C"` function that casts the pointer back:

```rust
use std::ffi::c_void;

extern "C" fn trampoline<F: FnMut(i32)>(item: i32, data: *mut c_void) {
    let closure = unsafe { &mut *(data as *mut F) };
    closure(item);
}

extern "C" {
    fn visit_all(
        cb: extern "C" fn(i32, *mut c_void),
        user_data: *mut c_void,
    );
}

fn visit<F: FnMut(i32)>(mut f: F) {
    unsafe {
        visit_all(trampoline::<F>, &mut f as *mut F as *mut c_void);
    }
}
```

Now callers write `visit(|x| total += x)` and never see a raw pointer. Each distinct closure type gets its own monomorphized trampoline, so the cast back to `F` is guaranteed to match.

## Lifetime rules you must uphold

The compiler cannot check what C does with your pointer. You have to reason about it:

- **Synchronous callbacks** (called only during `visit_all`) are the easy case. Borrowing `&mut f` on the stack is fine because the closure outlives the call.
- **Stored callbacks** (called later, from `register_callback`-style APIs) need the closure to live on the heap. Use `Box::into_raw` to hand ownership to C, and `Box::from_raw` in a matching "unregister" or "destroy" path to reclaim it. Forget the second half and you leak. Do it twice and you double free.
- **Threads.** If C may invoke the callback from another thread, require `F: Send` (and `Sync` if calls may overlap). The trampoline signature above does not enforce this, so add the bounds yourself.

## Panics must not cross the boundary

Unwinding out of a Rust function into C code is a real hazard. Since Rust 1.81, a panic that tries to escape an `extern "C"` function aborts the process rather than invoking UB. That is safer, but an abort is still probably not what your users want. Catch it deliberately:

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};

extern "C" fn trampoline<F: FnMut(i32)>(item: i32, data: *mut c_void) {
    let result = catch_unwind(AssertUnwindSafe(|| {
        let closure = unsafe { &mut *(data as *mut F) };
        closure(item);
    }));
    if result.is_err() {
        // Record the failure somewhere C can observe it,
        // e.g. a flag in your context struct, or an error code.
    }
}
```

If you want unwinding to be legal across the boundary, the ABI string is `extern "C-unwind"`, but both sides must be compiled with compatible unwinding support. Most C libraries are not, so catching is the safer default.

## Going the other direction

Exporting a Rust function for C to call is the mirror image. Add `#[no_mangle]` (written `#[unsafe(no_mangle)]` in edition 2024) so the symbol name stays predictable:

```rust
#[unsafe(no_mangle)]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}
```

Stick to FFI-safe types in the signature: primitives, raw pointers, `#[repr(C)]` structs, and `Option` of a function pointer or reference. Avoid `String`, `Vec`, `&str`, and trait objects, none of which have a stable C layout.

## A short checklist

1. Use `extern "C"` on every callback, never a plain `fn`.
2. Wrap nullable function pointers in `Option`.
3. Use a `void*` plus a generic trampoline to carry closures.
4. Decide who owns the context and when it is freed.
5. Add `Send`/`Sync` bounds if threads are involved.
6. Catch panics at the boundary.
7. Keep signatures to `#[repr(C)]`-compatible types.

## Wrapping up

Function pointers across FFI are not hard, but they punish sloppiness. The type system gives you a lot of help on the Rust side: distinct ABI types, non-null guarantees, monomorphized trampolines. The rest is discipline about ownership and unwinding. Get those right, and you can wrap a callback-heavy C API in a clean, closure-friendly Rust interface that hides every `unsafe` block behind a safe function.

If you have run into a nasty callback bug at the boundary, I would love to hear about it in the comments.
