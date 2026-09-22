# Workstation Management With Nix Flakes: Jupyter Notebook Example

Reproducing a Jupyter notebook is rarely as simple as copying the `.ipynb` file. The notebook might depend on a particular Python version, on native libraries or command-line utilities, or on package versions somebody installed months ago. A collaborator opens it on another machine and finds out a module is missing - or that a newer dependency gives different results.

Nix flakes are a practical way to describe the whole development environment as code. Instead of writing down a long list of installation steps, we can commit a small configuration that gives every machine the same Python and Jupyter setup. In this post we'll build a reproducible Jupyter Lab setup with Python, NumPy, pandas, Matplotlib and ipykernel.

## What Nix Adds

Python projects usually manage dependencies with `venv`, `pip`, Poetry, or Conda. These tools are useful, but they generally start working only once a compatible Python interpreter and the system libraries it needs are already there.

Nix works a level below that. It can manage:

- The Python interpreter
- Python packages
- Jupyter Lab
- Native libraries and command-line programs
- Environment variables
- Tool versions used by the project

A flake gives this environment a defined entry point, and it records its upstream inputs in a lock file. What you get is a project you can check out on any other machine with Nix and enter with one command. You don't have to install any of the project's tools globally, either. Each repository gets its own tools without touching the rest of the workstation.

## Prerequisites

You need Nix installed with flakes enabled. Recent Nix installations commonly turn flakes on through configuration, but if yours doesn't, add this to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

Restart any running Nix daemon or terminal sessions after you change it.

Check the installation:

```bash
nix --version
```

Then make a directory for the example:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
git init
```

Flakes generally only see files that Git is tracking, so we'll add the configuration to Git once it exists.

## The Flake

Create a file named `flake.nix`:

```nix
{
  description = "Reproducible Jupyter Lab environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        python = pkgs.python312.withPackages (
          pythonPackages: with pythonPackages; [
            jupyterlab
            ipykernel
            numpy
            pandas
            matplotlib
          ]
        );
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.git
          ];

          shellHook = ''
            echo "Jupyter development environment"
            echo "Python: $(python --version)"
            echo "Start Jupyter Lab with: jupyter lab"
          '';
        };
      }
    );
}
```

Add it to Git:

```bash
git add flake.nix
```

Now enter the environment:

```bash
nix develop
```

The first time can take a while, because Nix has to fetch metadata and build or download the packages. After that it's normally much faster, since those artifacts are kept in the local Nix store.

The shell hook should print the Python version and remind you how to start Jupyter.

## Reading the Configuration

The `inputs` section declares the external sources the flake uses:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
};
```

`nixpkgs` is the package collection we get Python, Jupyter, Git, and the Python libraries from. The name `nixos-unstable` refers to a moving branch, but the flake will lock it to a specific revision (more on that below).

`flake-utils` helps produce outputs for several common platforms. That means the same configuration can expose a development shell on x86-64 Linux, ARM Linux, and macOS, as long as the packages are available there.

Inside `outputs`, the selected `nixpkgs` revision is imported for the current platform:

```nix
pkgs = import nixpkgs {
  inherit system;
};
```

Then the Python environment is built with `withPackages`:

```nix
python = pkgs.python312.withPackages (
  pythonPackages: with pythonPackages; [
    jupyterlab
    ipykernel
    numpy
    pandas
    matplotlib
  ]
);
```

This gives you a single Python interpreter whose import path includes the listed packages. There's no separate `pip install` step, and nothing gets installed into your home directory.

Last, `pkgs.mkShell` defines what shows up when we run `nix develop`. Here that's our configured Python distribution and Git. You can add other non-Python tools to the `packages` list later.

## Locking It Down

`flake.lock` is created by the first `nix develop`. Take a look at the repository:

```bash
git status
```

You should see both `flake.nix` and `flake.lock`. Commit them together:

```bash
git add flake.nix flake.lock
git commit -m "Add reproducible Jupyter environment"
```

`flake.nix` describes which inputs the project wants, and `flake.lock` records the exact revision picked for each one.

This is the important bit. If all we had was a reference to `nixos-unstable`, two developers entering the project at different times could end up with different package sets. With the lock file committed, both machines resolve the same `nixpkgs` revision.

When you do want to update the locked inputs, run:

```bash
nix flake update
```

Then inspect and test the changes before you commit the new lock file. That way a dependency upgrade shows up as a change in the repository, instead of as some invisible difference between two machines.

## Running Jupyter Lab

Enter the development shell if you aren't in it already:

```bash
nix develop
```

Start the server:

```bash
jupyter lab
```

Jupyter will print a local URL, usually with an authentication token in it. Open that URL in a browser and create a Python notebook.

Here's a small example to test the environment:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

samples = pd.DataFrame({
    "x": np.arange(0, 10),
    "y": np.arange(0, 10) ** 2,
})

samples.plot(x="x", y="y", marker="o")
plt.show()
```

The notebook kernel is launched from the shell Nix provides, so the imports just work without installing anything from inside Jupyter.

When you're done, stop Jupyter and leave the shell:

```bash
exit
```

Outside the development shell, `jupyter` doesn't need to exist at all. The dependency belongs to the project, and it never becomes a permanent part of the workstation.

## Skipping the Shell

Interactive shells are handy while you're working, but Nix can also run a command directly:

```bash
nix develop --command jupyter lab
```

This comes in useful in scripts, documentation or editor configuration, because the command explicitly runs inside the flake's environment.

You can check the Python version the same way:

```bash
nix develop --command python --version
```

Or run an analysis script you've checked in:

```bash
nix develop --command python analysis.py
```

Commands like these make fewer assumptions about whatever shell the caller happens to be in.

## Loading It Automatically

If you switch between projects a lot, it's easy to forget to type `nix develop` every time. `direnv` can load and unload environments for you as you enter and leave a directory.

Install `direnv` however you like to install workstation-level tools, turn on its shell integration, and create `.envrc` in the project:

```bash
use flake
```

Then authorize it:

```bash
direnv allow
```

From then on, entering the directory loads the flake environment, and leaving it puts your previous shell environment back.

Commit `.envrc` so your collaborators get the same behavior:

```bash
git add .envrc
git commit -m "Load development shell with direnv"
```

The authorization itself stays local, though. A checked-in `.envrc` isn't automatically trusted on another machine, which stops a repository from quietly running shell instructions you just downloaded.

## Adding Dependencies

Say the notebook later needs SciPy and Seaborn. Add them to the Python package list:

```nix
python = pkgs.python312.withPackages (
  pythonPackages: with pythonPackages; [
    jupyterlab
    ipykernel
    numpy
    pandas
    matplotlib
    scipy
    seaborn
  ]
);
```

Leave the development shell and enter it again, or reload `direnv`. Nix builds a new one with the bigger package set - it doesn't change the old one in place.

System tools go in the shell's `packages` list. A notebook that converts documents or processes images, for example, might need Pandoc and ImageMagick:

```nix
devShells.default = pkgs.mkShell {
  packages = [
    python
    pkgs.git
    pkgs.pandoc
    pkgs.imagemagick
  ];
};
```

To me this is one of the biggest advantages over a Python-only dependency file: the repository can declare the executables it needs right next to the Python libraries.

## Checking the Flake

Before you share changes, validate the flake:

```bash
nix flake check
```

You can also look at its outputs:

```bash
nix flake show
```

You should see a default development shell for your system in there.

For a small notebook repository, a `.gitignore` like this is a good start:

```gitignore
.direnv/
.ipynb_checkpoints/
__pycache__/
```

Don't ignore `flake.lock`! It's part of what makes this reproducible, and you should normally commit it.

## What Nix Can't Do

Nix makes the environment reproducible, but it can't promise every notebook result will be identical. An analysis can also depend on:

- Input datasets
- Random seeds
- Network services
- Hardware-specific numerical behavior
- Execution order within the notebook
- External credentials or secrets

So data versioning and deterministic notebook habits still matter. Record your random seeds, don't lean on hidden notebook state, and write down where external data comes from.

Keep secrets out of `flake.nix`, `flake.lock`, `.envrc` and the notebook. Pass them in at runtime with a proper secret-management mechanism.

It's also worth checking whether a package is available before you mix Nix-managed Python packages with `pip install`. Installing one-off packages into the environment works against the declarative model, and it can fail when native extensions expect libraries in the usual filesystem locations. Where you can, declare dependencies in the flake so every workstation takes the same path.

## Day to Day

Once it's set up, the daily workflow is small:

```bash
git clone <repository>
cd <repository>
nix develop
jupyter lab
```

The committed lock file makes sure your collaborators, and any machine you set up in the future, resolve the same package-set revision. Everything the notebook needs, from the Python interpreter and notebook server down to the libraries and supporting tools, is defined in the repository with it. Installation instructions turn into configuration you can run, and upgrades turn into changes you can review. Your project's tools stop depending on the accidental history of one particular machine. Neat!
