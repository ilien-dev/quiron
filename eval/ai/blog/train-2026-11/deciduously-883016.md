# Workstation Management With Nix Flakes: Build a CMake C++ Package

Every developer has a story about a build that worked yesterday and fails today. Maybe a system library updated, a compiler moved to a new major version, or a teammate installed CMake from a different source. Nix is a package manager built to make those failures rare. Flakes add a standard way to pin inputs and describe a project's build and development environment in one file.

In this post we'll package a small C++ project built with CMake using a Nix flake. We'll get a reproducible build, a development shell with the same toolchain, and a lock file that keeps both stable across machines. The approach works for a single laptop and for a team.

> **Platform note:** Nix doesn't run natively on Windows. If you're on Windows 11, install WSL2 with a Linux distribution such as Ubuntu, then install Nix inside that environment. Everything below runs in a Linux shell, including the WSL2 terminal.

## Why Flakes?

Traditional Nix expressions work, but they have a weak point: nothing pins the version of `nixpkgs` you're importing. Two people can run the same `default.nix` and get different results depending on which channel they subscribed to.

A flake solves this with two things:

1. **Declared inputs**, such as `nixpkgs` and any helper libraries, referenced in `flake.nix`.
2. **A lock file**, `flake.lock`, that records the exact revision of every input.

Commit both files, and anyone who checks out your repository gets the same package set, the same compiler, and the same CMake version. Updating dependencies becomes an explicit step rather than a surprise.

## Enabling Flakes

Flakes are still marked as experimental in most Nix installations. Enable them by adding this to `~/.config/nix/nix.conf` (create the file if needed):

```ini
experimental-features = nix-command flakes
```

Restart the Nix daemon if your installation uses one, then confirm the setup works:

```bash
nix --version
nix flake --help
```

## The Project

Create a new directory with a tiny C++ program and a CMake build:

```
hello-cmake/
├── CMakeLists.txt
├── flake.nix
└── src/
    └── main.cpp
```

`src/main.cpp`:

```cpp
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    std::string name = (argc > 1) ? argv[1] : "workstation";
    std::cout << "Hello from a Nix-built CMake project, " << name << "!\n";
    return 0;
}
```

`CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(hello_cmake LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(hello src/main.cpp)

install(TARGETS hello RUNTIME DESTINATION bin)
```

Nothing in this CMake file is Nix-specific. That's intentional. The flake wraps the existing build rather than replacing it, so the project still builds with plain CMake on any machine that has it.

## Writing the Flake

Now the main file, `flake.nix`:

```nix
{
  description = "hello-cmake: a CMake C++ package managed by Nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "hello-cmake";
          version = "0.1.0";

          src = ./.;

          nativeBuildInputs = [ pkgs.cmake ];

          cmakeBuildType = "Release";
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.default ];

          packages = [
            pkgs.ninja
            pkgs.clang-tools
            pkgs.gdb
          ];
        };

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/hello";
        };
      });
}
```

Let's walk through the important parts.

**`inputs`** declares where dependencies come from. `nixpkgs` provides the packages. `flake-utils` is a small helper library that lets us write the outputs once and generate them for each supported system (`x86_64-linux`, `aarch64-darwin`, and so on) without copy-pasting.

**`packages.default`** defines how to build the project. `pkgs.stdenv.mkDerivation` is the standard Nix build helper. Nixpkgs' CMake setup hook takes care of the configure, build, and install phases when `cmake` appears in `nativeBuildInputs`. We only need to supply the source tree and metadata. `cmakeBuildType` sets the build type without us writing the flag by hand.

**`devShells.default`** creates a development environment. `inputsFrom` pulls in the build dependencies of the package, so the shell has the same CMake and compiler the package uses. We then add tools we only want while developing: Ninja for faster builds, `clang-tools` for `clangd` and `clang-format`, and `gdb` for debugging.

**`apps.default`** makes `nix run` work. It points at the built binary so the project can be executed directly.

## Locking Dependencies

Generate the lock file:

```bash
cd hello-cmake
git init
git add .
nix flake lock
```

Flakes only see files tracked by Git, so `git add` matters here. The `nix flake lock` command resolves `nixpkgs` and `flake-utils` to specific commits and writes them to `flake.lock`:

```json
"nixpkgs": {
  "locked": {
    "lastModified": 1762000000,
    "narHash": "sha256-...",
    "owner": "NixOS",
    "repo": "nixpkgs",
    "rev": "...",
    "type": "github"
  }
}
```

The exact revision is what makes the setup reproducible. Commit `flake.lock` along with your other files. When a teammate runs a build six months from now, they get the same compiler, the same CMake version, and the same library set.

To update everything to the latest revisions later:

```bash
nix flake update
```

To update a single input:

```bash
nix flake lock --update-input nixpkgs
```

Updates are then a reviewable diff in version control, not something that happens quietly.

## Building the Package

Build the project:

```bash
nix build
```

Nix builds the package in an isolated sandbox. It doesn't read anything from your home directory or from system-wide libraries, which is the main reason builds are reproducible. When it finishes, `result` is a symlink into the Nix store:

```bash
./result/bin/hello Jesus
# Hello from a Nix-built CMake project, Jesus!
```

Because the output lives in the Nix store under a hash of its inputs, two builds with identical inputs produce identical outputs. If you change the compiler, the CMake version, or a single source file, the hash changes and Nix rebuilds only what's needed.

Run it directly with:

```bash
nix run . -- Workstation
```

## Working in the Development Shell

Enter the development environment:

```bash
nix develop
```

Your prompt now runs inside a shell that has CMake, the compiler, Ninja, `clangd`, and `gdb` available. Nothing was installed globally, and nothing leaks into other projects. Build in the usual way:

```bash
cmake -S . -B build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build
./build/hello
```

The `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` flag writes `compile_commands.json`, which lets `clangd` in your editor understand the project. Since the shell provides `clangd` through `clang-tools`, editor integration works without any manual setup.

If you prefer to automate shell entry, `direnv` with a one-line `.envrc` containing `use flake` loads the development shell whenever you `cd` into the project.

## Checking the Flake

Before committing changes, verify the flake evaluates and the outputs build:

```bash
nix flake check
```

This evaluates every output in `flake.nix` and reports errors early. You can also inspect what the flake provides:

```bash
nix flake show
```

This lists `packages`, `devShells`, and `apps` for each system, which is useful when reviewing changes.

## What This Gives a Workstation

The flake is a small file, but it changes how the project lives on a machine:

- **Toolchain pinning.** The compiler, CMake, and debugger come from `flake.lock`, not from whatever happens to be installed.
- **Isolation.** Dependencies don't leak in from unrelated projects, and the build doesn't depend on hidden global state.
- **Onboarding.** A new machine needs Nix and one command, `nix develop`, instead of a setup document with a dozen steps.
- **Auditable upgrades.** A compiler update appears as a change to `flake.lock`, which you can review and revert.

For a personal workstation, you can extend the same idea to your whole machine with tools like Home Manager or NixOS modules. For this project, a flake alone already covers the build and the development environment.

## Common Pitfalls

A few things tend to trip people up:

- **Forgetting `git add`.** Flakes read from Git, so new files must be tracked, at least staged, before Nix sees them.
- **Missing experimental flags.** If `nix build` reports an unknown command, check `nix.conf` for `experimental-features`.
- **Assuming system libraries are visible.** Inside the sandbox they aren't. Declare every dependency in `nativeBuildInputs` (build tools) or `buildInputs` (libraries the program links against).
- **Ignoring the lock file.** Deleting `flake.lock` to "fix" a problem silently updates every dependency. Update inputs deliberately instead.

## Conclusion

We packaged a CMake C++ project with a Nix flake and got three things from one file: a reproducible build, a development shell with a pinned toolchain, and a lock file that makes updates explicit. The CMake project itself didn't change, so you can adopt this approach incrementally in any existing repository.

From here you could add tests with CTest, package a library for other flakes to consume, or cross-compile for another architecture. Each builds on the same foundation: declared inputs, locked revisions, and isolated builds.

Start with `nix flake init` in an existing project, or copy the files above, and run `nix develop`. Your next workstation setup could be a single command.
