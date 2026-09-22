# Rust Function Pointers Across FFI Boundaries

One of the trickier things you'll eventually run into when writing Rust code that talks to C is passing function pointers across the FFI boundary. It comes up more often than you'd expect: registering a callback with a C library, setting up an event handler, or implementing a plugin system where the host application calls back into your Rust code. Let's walk through how this actually works, and the gotchas that tend to trip people up.

## The Basic Setup

Rust function pointers are represented by the `fn` type, and when compiled with a compatible calling convention, they map directly onto C function pointers. Here's a minimal example of a Rust function meant to be called from C:

```rust
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

Two things matter here. First, `extern "C"` tells the compiler to use the C calling convention rather than Rust's own, which isn't stable or guaranteed to match C's ABI. Second, `#[no_mangle]` prevents Rust from mangling the function's name, so it's exported under the exact symbol `add` that C code expects to link against.

## Passing Function Pointers as Arguments

Where things get more interesting is when you want to pass a Rust function as a callback into a C function, or accept a C function pointer in Rust. Suppose you have a C function with this signature:

```c
void register_callback(int (*callback)(int));
```

In Rust, you'd declare the corresponding extern block like this:

```rust
extern "C" {
    fn register_callback(callback: extern "C" fn(i32) -> i32);
}
```

And then define a Rust function with a matching signature to pass in:

```rust
extern "C" fn my_callback(x: i32) -> i32 {
    x * 2
}

fn main() {
    unsafe {
        register_callback(my_callback);
    }
}
```

Notice that `my_callback` also needs the `extern "C"` qualifier. Without it, the compiler will use Rust's calling convention, and the resulting function pointer won't be compatible with what the C side expects. This is an easy mistake to make and the compiler won't always catch it clearly, especially if the mismatch happens across a build boundary where C headers aren't checked against Rust's type signatures.

## Passing Closures Is Harder Than It Looks

A common instinct is to try passing a Rust closure as a callback, especially one that captures some state. This doesn't work directly, because C function pointers are just addresses with no notion of captured environment. A Rust closure that captures variables is a different, fatter type under the hood, and it can't be coerced into a bare `extern "C" fn` pointer.

The usual workaround is to pass a `void*` style user data pointer alongside the function pointer, which is a pattern you'll recognize from plenty of C libraries:

```c
void register_callback(int (*callback)(int, void*), void* user_data);
```

You stash your Rust state behind a raw pointer, cast it appropriately in the callback, and rehydrate it on the Rust side. It's unsafe, and you're responsible for ensuring the lifetime of that pointer outlives every call the C code might make.

## Watch Your Panics

One subtlety that catches people off guard: if your `extern "C"` function panics, unwinding across an FFI boundary is undefined behavior. C doesn't know what a Rust panic is, and letting one propagate into C stack frames can corrupt program state in ways that are extremely painful to debug. The fix is to wrap the body of any callback that might panic in `std::panic::catch_unwind`, convert the panic into an error code or sentinel value, and return that instead of letting it unwind further.

```rust
extern "C" fn safe_callback(x: i32) -> i32 {
    std::panic::catch_unwind(|| {
        risky_operation(x)
    }).unwrap_or(-1)
}
```

## Wrapping Up

Function pointers across FFI boundaries are one of those areas where Rust's safety guarantees mostly step aside and hand responsibility back to you. Match your calling conventions, be deliberate about how you smuggle state through raw pointers, and always guard against unwinding panics at the boundary. Get those three things right and callback-based C interop becomes a lot less scary than it first appears.
