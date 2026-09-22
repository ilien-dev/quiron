# Workstation Management With Nix Flakes: Build a Cmake C++ Package

Nix is a powerful but often complex package manager and configuration language that allows you to describe your development environment with precision. Nix Flakes, introduced as an experimental feature and now widely adopted, makes managing reproducible development environments significantly easier. In this guide, I'll walk you through building and managing a C++ project using CMake with Nix Flakes.

## What is Nix and Why Flakes?

Nix is a purely functional package manager that builds software in isolation from other packages. This means you can have multiple versions of the same dependency installed without conflicts. Each package is built in its own sandbox with only the dependencies it explicitly declares.

Nix Flakes extend this with a standardized interface for describing projects and their dependencies. Instead of complex setup.nix files, Flakes provide a structured approach to defining inputs (dependencies), outputs (what your project produces), and a flake.lock file that ensures reproducibility.

The main advantage is that every developer on your team, and your CI/CD system, will have identical development and build environments. No more "but it works on my machine" problems.

## Prerequisites

First, install Nix if you haven't already. The recommended approach is to use the Determinate Systems installer, which provides a more user-friendly installation than the standard one:

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

Enable Flakes by adding this to your Nix configuration. If you're using Determinate Systems, Flakes should be enabled by default.

Verify your setup:

```bash
nix --version
nix flake --help
```

## Creating Your Project Structure

Create a new directory for your C++ project:

```bash
mkdir my-cpp-project
cd my-cpp-project
```

Initialize git (Flakes work best with a git repository):

```bash
git init
```

Create your basic project structure:

```
my-cpp-project/
├── flake.nix
├── CMakeLists.txt
├── src/
│   └── main.cpp
└── include/
    └── myheader.h
```

## Writing the Flake

The flake.nix file is where you describe your project. Here's a comprehensive example:

```nix
{
  description = "C++ development environment with CMake";

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
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            cmake
            gcc
            gdb
            clang-tools
            git
          ];

          shellHook = ''
            echo "C++ development environment loaded"
          '';
        };

        packages.default = pkgs.stdenv.mkDerivation {
          name = "my-cpp-project";
          src = self;

          buildInputs = with pkgs; [ cmake gcc ];

          buildPhase = ''
            cmake -B build
            cmake --build build
          '';

          installPhase = ''
            mkdir -p $out/bin
            cp build/my-cpp-project $out/bin/
          '';
        };
      }
    );
}
```

Let's break this down:

- `inputs`: Declares what your flake depends on. We're using nixpkgs (the Nix package repository) and flake-utils (utilities for working with multiple systems).
- `outputs`: What your flake produces. We define a development shell and a package.
- `devShells.default`: The environment you enter when running `nix develop`. It includes CMake, GCC, GDB, and other development tools.
- `packages.default`: Instructions for building your project. This is run when you execute `nix build`.

## Setting Up CMakeLists.txt

Create a basic CMakeLists.txt for your C++ project:

```cmake
cmake_minimum_required(VERSION 3.10)
project(my-cpp-project)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(my-cpp-project
    src/main.cpp
)
```

## Using Your Development Environment

Now you can enter the development environment:

```bash
nix flake update
nix develop
```

This command drops you into a shell where CMake, GCC, and all dependencies are available. Your environment is completely isolated from your system, but within the shell, everything works as expected.

Build your project:

```bash
cmake -B build
cmake --build build
```

Run your executable:

```bash
./build/my-cpp-project
```

## Building with Nix

To build your project using Nix's build system:

```bash
nix build
```

This creates a result symlink pointing to your built project. This build is fully reproducible—running it again will produce identical output.

## Managing Dependencies

As your project grows, you'll need additional libraries. Add them to your flake.nix:

```nix
buildInputs = with pkgs; [
  cmake
  gcc
  gdb
  clang-tools
  git
  boost
  openssl
];
```

Then run `nix flake update` to update your flake.lock with the new dependencies.

## CI/CD Integration

Flakes are ideal for CI/CD. Your CI system can use `nix build` with confidence that it's building in the exact same environment as your local machine.

On GitHub Actions, you can use the official Nix action:

```yaml
- uses: DeterminateSystems/nix-installer-action@main
- run: nix build
```

## Conclusion

Nix Flakes provide a declarative, reproducible way to manage C++ development environments. While the learning curve exists, the payoff is significant: perfect environment consistency across your team, eliminated dependency conflicts, and reproducible builds. Start with this guide, explore the Nix manual when you need more advanced features, and enjoy the confidence that comes with truly reproducible software development.