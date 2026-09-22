# Workstation Management With Nix Flakes: Jupyter Notebook Example

I recently started a class that uses Python and [Jupyter](https://jupyter.org/).  The first assignment just needed to import `numpy` and `pandas`, which usually means reaching for `pip`.  My problem with that is that `pip` installs packages globally by default.  The standard fix is a `virtualenv` plus a `requirements.txt`, and in my experience that setup is brittle and non-portable, and it leaves clutter everywhere.

[Nix](https://nixos.org/) solves this.  It's a tool for managing environments that is declarative, reproducible, and unified - you describe what a project needs in one file, and you get exactly that, the same way every time.  This post walks through the environment I'm using for the class.

## Getting Nix

Nix runs on Linux (i686, x86_64, and aarch64) and on macOS.  On macOS it's x86_64 only for now, though ARM support is expected.  The [Quick Start](https://nixos.org/manual/nix/stable/#chap-quick-start) in the manual covers installation.

This example uses Nix Flakes, which you need to enable yourself.  The [NixOS wiki page on Flakes](https://nixos.wiki/wiki/Flakes) explains how - if you're not on NixOS, look at the "Non-NixOS" section.  For most setups it comes down to this line in `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

For what it's worth, I think NixOS is the best way to use Nix.  I wiped my drive recently, and one command brought back an identical system.  My config is [on GitHub](https://github.com/deciduously/nixos-config) if you're curious.  You don't need NixOS for anything in this post, though.

## The Flake

Here's the whole thing.  Put it in a file called `flake.nix` in your project directory:

```nix
{
  description = "Jupyter environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3.withPackages (ps: with ps; [
          ipython
          jupyter
          numpy
          pandas
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [ python ];
          shellHook = ''
            jupyter notebook
          '';
        };
      }
    );
}
```

That's the entire configuration, under 30 lines.  Then run:

```bash
nix develop
```

The first run is slow because Nix has to download everything, but after that it's quick.  You end up in a shell with Python and the libraries available, and the `shellHook` starts `jupyter notebook` for you.

Flakes only see files that Git knows about, so run `git add flake.nix` before you try this.

## What's Going On

There are two inputs: `nixpkgs` is the package collection, and I'm pointing it at the `nixos-unstable` branch.  `flake-utils` comes from numtide, and its `eachDefaultSystem` function generates outputs for each of the common systems so the same file works on whatever machine you're using (mine is `x86_64-linux`).

Inside `outputs`, `python3.withPackages` gives us a Python interpreter that already has `ipython`, `jupyter`, `numpy`, and `pandas` on its import path.  There's no separate `pip install` step.  If you need a specific Python version, you can pin it by swapping in something like `python39` for `python3`.  You can look up available packages with the [package search](https://search.nixos.org/packages).

`mkShell` builds the development shell that `nix develop` drops you into.  The [nix-shell page on the wiki](https://nixos.wiki/wiki/Development_environment_with_nix-shell) has more on what it can do.  The `shellHook` is just shell code that runs when you enter - mine starts Jupyter, but it can be anything you like.  It could make you a `cool_file.txt` every time, if that's what you're into.

## A Few Things to Know

The Nix store keeps everything you've downloaded, and it grows over time.  When it gets too big `nix-collect-garbage` removes whatever is no longer referenced.

The first `nix develop` also writes a `flake.lock`, which records the exact revisions of your inputs.  Commit it with `flake.nix` and collaborators get the same package set you did.  When you do want newer packages, run:

```bash
nix flake update
```

That refreshes the hashes in `flake.lock`.

## Next Time

This was only the development shell - in upcoming posts I want to get into packaging software with Nix, using flakes to manage a whole operating system, and how Nix works under the hood.

*Cover photo by CHUTTERSNAP on Unsplash*
