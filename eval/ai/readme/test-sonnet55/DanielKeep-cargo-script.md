# cargo-script

**Cargo script subcommand.** Run Rust source files and one-off expressions as if they were scripts, with no project setup and no hand-written `Cargo.toml`.

```console
$ cargo script hello.rs
Hello, world!
```

---

## Table of contents

- [Why cargo-script?](#why-cargo-script)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Embedded manifests](#embedded-manifests)
- [Expressions and stream processing](#expressions-and-stream-processing)
- [Caching](#caching)
- [Command-line reference](#command-line-reference)
- [Shebang support](#shebang-support)
- [Environment variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Why cargo-script?

Rust is a great language for small tools, but the ceremony of `cargo new`, editing a manifest, and building a project is heavy when all you want is to try an idea or automate a chore. `cargo-script` removes that overhead:

- **Single-file programs.** Write one `.rs` file and run it.
- **Inline dependencies.** Declare crates in a comment block at the top of the file.
- **Expression evaluation.** Evaluate a Rust expression straight from the command line.
- **Stream processing.** Apply a closure to every line of standard input.
- **Fast reruns.** Compiled artifacts are cached, so unchanged scripts start almost instantly.

## Installation

### From crates.io

```console
cargo install cargo-script
```

Cargo places the binary in `~/.cargo/bin` (or `%USERPROFILE%\.cargo\bin` on Windows). Make sure that directory is on your `PATH`. Once installed, Cargo discovers it automatically and you can call it as `cargo script`.

### From source

```console
git clone <repository-url>
cd cargo-script
cargo install --path .
```

### Requirements

- A working Rust toolchain (stable is sufficient), installed via [rustup](https://rustup.rs).
- A linker and C toolchain appropriate for your platform, the same as for any Rust project.

Verify the installation:

```console
cargo script --version
```

## Quick start

Create a file named `hello.rs`:

```rust
fn main() {
    println!("Hello, world!");
}
```

Run it:

```console
cargo script hello.rs
```

Pass arguments to your program after the script name. Use `--` if an argument could be mistaken for a `cargo-script` flag:

```console
cargo script greet.rs -- --name Ferris
```

Your script reads them with `std::env::args()` as usual:

```rust
fn main() {
    for arg in std::env::args().skip(1) {
        println!("arg: {arg}");
    }
}
```

## Embedded manifests

Scripts can declare dependencies and package metadata in a fenced block inside a doc comment at the top of the file. The block is ordinary `Cargo.toml` syntax:

````rust
//! ```cargo
//! [dependencies]
//! regex = "1"
//! chrono = "0.4"
//! ```

use regex::Regex;

fn main() {
    let re = Regex::new(r"\d{4}-\d{2}-\d{2}").unwrap();
    let today = chrono::Local::now().format("%Y-%m-%d").to_string();
    println!("{}", re.is_match(&today));
}
````

Anything valid in a manifest can go in the block: features, edition, profile settings, and so on.

````rust
//! ```cargo
//! [package]
//! edition = "2021"
//!
//! [dependencies]
//! serde = { version = "1", features = ["derive"] }
//! serde_json = "1"
//!
//! [profile.release]
//! opt-level = 3
//! ```
````

If you omit the block, the script is compiled with no dependencies beyond the standard library.

## Expressions and stream processing

For quick calculations you don't even need a file.

### Evaluate an expression

```console
$ cargo script --expr "6 * 7"
42

$ cargo script --expr "(1..=10).sum::<u32>()"
55
```

The result is printed using its `Debug` representation.

### Run a block

```console
cargo script --expr "{ let v = vec![3, 1, 2]; let mut v = v; v.sort(); v }"
```

### Process lines from standard input

`--loop` runs a closure once per input line. The current line is bound to `line`:

```console
$ printf "apple\nbanana\ncherry\n" | cargo script --loop "println!(\"{}\", line.to_uppercase())"
APPLE
BANANA
CHERRY
```

Use `--count` to also receive a 1-based line counter named `n`:

```console
$ ls | cargo script --loop --count "println!(\"{n}: {line}\")"
```

Combine `--loop` with `--dep` to pull in crates for one-liners:

```console
cat log.txt | cargo script --dep regex=1 --loop \
  "if regex::Regex::new(\"ERROR\").unwrap().is_match(&line) { println!(\"{line}\"); }"
```

## Caching

Compiling on every invocation would be slow, so `cargo-script` keeps a cache keyed on:

- the script contents,
- the embedded manifest,
- the active toolchain, and
- the build profile.

When none of these change, the cached binary is reused. When something does change, only that script is rebuilt. Dependencies are shared between scripts where possible, so adding a second script that uses `regex` doesn't recompile `regex`.

Default cache locations:

| Platform | Location                              |
| -------- | ------------------------------------- |
| Linux    | `~/.cache/cargo-script`               |
| macOS    | `~/Library/Caches/cargo-script`       |
| Windows  | `%LOCALAPPDATA%\cargo-script\cache`   |

Manage the cache with:

```console
cargo script --clear-cache      # remove everything
cargo script --cache-path       # print the cache directory
```

## Command-line reference

```text
cargo script [OPTIONS] <SCRIPT> [-- <ARGS>...]
cargo script [OPTIONS] --expr <EXPR>
cargo script [OPTIONS] --loop <CLOSURE>
```

| Option                   | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `-e`, `--expr <EXPR>`    | Evaluate a Rust expression and print the result.                 |
| `-l`, `--loop <BODY>`    | Run `BODY` for each line of stdin, with the line bound to `line`.|
| `-c`, `--count`          | With `--loop`, also bind a 1-based counter named `n`.            |
| `-d`, `--dep <NAME=VER>` | Add a dependency. May be repeated.                               |
| `--release`              | Build with optimizations.                                        |
| `--features <LIST>`      | Enable the given crate features, comma separated.                |
| `--toolchain <NAME>`     | Use a specific rustup toolchain, such as `nightly`.              |
| `--offline`              | Do not access the network when resolving dependencies.           |
| `--force`                | Ignore the cache and rebuild.                                    |
| `--build-only`           | Compile the script but do not run it.                            |
| `--clear-cache`          | Delete all cached build artifacts and exit.                      |
| `--cache-path`           | Print the cache directory and exit.                              |
| `-v`, `--verbose`        | Show the underlying Cargo invocation and build output.           |
| `-h`, `--help`           | Print help.                                                      |
| `-V`, `--version`        | Print version.                                                   |

The exit code of your script is propagated, so `cargo-script` behaves well in shell pipelines and CI jobs.

## Shebang support

On Unix-like systems, make scripts directly executable. Put this on the first line:

```rust
#!/usr/bin/env -S cargo script
```

Then:

```console
chmod +x tool.rs
./tool.rs
```

A complete example:

````rust
#!/usr/bin/env -S cargo script
//! ```cargo
//! [dependencies]
//! walkdir = "2"
//! ```

fn main() {
    let total = walkdir::WalkDir::new(".")
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .count();
    println!("{total} files");
}
````

The `-S` flag for `env` is required to pass multiple arguments and is available on modern GNU and BSD systems. The shebang line is ignored by the Rust compiler, so the file remains valid Rust.

## Environment variables

| Variable                  | Effect                                              |
| ------------------------- | --------------------------------------------------- |
| `CARGO_SCRIPT_CACHE_DIR`  | Override the cache directory.                       |
| `CARGO_SCRIPT_TOOLCHAIN`  | Default toolchain when `--toolchain` is not given.  |
| `CARGO_SCRIPT_LOG`        | Set to `debug` for detailed diagnostics.            |
| `CARGO_HOME`              | Respected for registry and download locations.      |

## Troubleshooting

**`error: no such subcommand: script`**
The binary is not on your `PATH`. Add Cargo's `bin` directory to it and restart your shell.

**A script rebuilds every time.**
Something in the cache key is changing, often a toolchain override or a generated file. Run with `--verbose` to see what Cargo is doing, and check `CARGO_SCRIPT_TOOLCHAIN`.

**Dependency resolution fails offline.**
Run the script once with network access so the crates are downloaded, then use `--offline`.

**Stale or corrupted build output.**
Run `cargo script --clear-cache` or use `--force` for a single run.

**Windows shebang scripts don't run directly.**
Windows ignores shebangs. Invoke the script with `cargo script tool.rs`.

## Contributing

Contributions are welcome. To get started:

1. Fork the repository and create a topic branch.
2. Make your change, adding tests where it makes sense.
3. Run the checks locally:
   ```console
   cargo fmt --all -- --check
   cargo clippy --all-targets -- -D warnings
   cargo test
   ```
4. Open a pull request describing the problem and your approach.

Bug reports are most useful with the output of `cargo script --version`, `rustc --version`, your operating system, and a minimal script that reproduces the problem.

## License

Licensed under either of

- Apache License, Version 2.0
- MIT license

at your option. Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project shall be dual licensed as above, without any additional terms or conditions.

---

I wrote this to be self-contained, so the flags, environment variables, and cache paths are illustrative. Check them against the actual implementation before publishing. Tell me if you'd like me to save it as `README.md` or adjust the tone and length.
