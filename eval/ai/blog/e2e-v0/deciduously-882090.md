# Workstation management with Nix flakes: Jupyter notebook example

Reproducing a Jupyter notebook is rarely as easy as just copying the `.ipynb` file.

The notebook might need a certain Python version, some native libraries or command-line tools, or package versions that got put on the box months ago. Then a collaborator opens it on another machine and finds a module missing, or a newer dependency gives different results.

Nix flakes are a practical way to describe the whole development environment as code. Instead of writing down a long list of install steps, we can commit a small config that gives every workstation the same Python and Jupyter setup.

In this tutorial I'll build a reproducible Jupyter Lab environment with Python, NumPy, pandas, Matplotlib and ipykernel.

## What Nix adds

Most Python projects manage dependencies with `venv`, `pip`, Poetry or Conda. Those tools are useful, but they generally start working only after a compatible Python interpreter and the system libraries you need are already there.

Nix works a level lower. It can manage all of this for us:

- The Python interpreter
- Python packages
- Jupyter Lab
- Native libraries and command-line programs
- Environment variables
- The versions of the tools the project uses

A flake gives this environment a defined entry point, and it records its upstream inputs in a lock file. What you get is a project that someone can check out on another machine with Nix and enter with one command.

We don't have to install the project's tools globally for this, and I like that a lot. Each repository can have its own environment and leave the rest of the workstation alone.

## Prerequisites

You need Nix installed with flakes turned on. Recent Nix installs commonly turn flakes on through config, but if yours doesn't, add this to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

After you change the config, restart any running Nix daemon and any open terminal sessions.

Check the install:

```bash
nix --version
```

Make a directory for the example:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
git init
```

Flakes generally only see files that Git tracks, so we'll add the config to Git once we've written it.

## Creating the flake

Create a file called `flake.nix`:

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

The first run can take a while, because Nix has to fetch metadata and build or download the packages. After that it's normally much faster, since those artifacts are kept in the local Nix store.

The shell hook should print the Python version and remind you how to start Jupyter.

## Understanding the configuration

The `inputs` section lists the outside sources the flake uses:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
};
```

`nixpkgs` is the package collection we get Python, Jupyter, Git and the Python libraries from. The name `nixos-unstable` points at a branch that moves, but the flake will lock it to one specific revision.

`flake-utils` helps build outputs for several common platforms. So the same config can give you a development shell on systems like x86-64 Linux, ARM Linux and macOS, as long as the packages are available there.

Inside `outputs`, we import the chosen `nixpkgs` revision for the current platform:

```nix
pkgs = import nixpkgs {
  inherit system;
};
```

Then we use `withPackages` to build the Python environment:

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

That gives you one Python interpreter whose import path includes the packages in the list. There's no separate `pip install` step, and nothing gets installed into your home directory.

Last, `pkgs.mkShell` sets up what we get when we run `nix develop`. Here that's our Python build and Git. You can add other tools that aren't Python to the `packages` list later on.

## Locking the environment

The first `nix develop` creates `flake.lock`. Take a look at the repository:

```bash
git status
```

You should see both `flake.nix` and `flake.lock`. Commit them together:

```bash
git add flake.nix flake.lock
git commit -m "Add reproducible Jupyter environment"
```

`flake.nix` says which inputs the project wants, and `flake.lock` records the exact revisions that were picked for them.

That difference matters. If you only had the `nixos-unstable` reference, two developers who entered the project at different times could get different package sets. With the lock file committed, both machines resolve the same `nixpkgs` revision.

When you actually want to update the locked inputs, run:

```bash
nix flake update
```

Then look over and test the changes before you commit the new lock file. That way a dependency upgrade shows up as a change in the repo, not as some invisible difference between two machines.

## Running the Jupyter Lab server

Enter the dev shell if you aren't in it already:

```bash
nix develop
```

Start the server:

```bash
jupyter lab
```

Jupyter prints a local URL, usually with an auth token in it. Open that URL in a browser and create a Python notebook.

I like to test the environment with a small example:

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

The notebook kernel starts from the environment Nix provides, so the imports work without you installing anything from inside Jupyter.

When you're done, stop Jupyter and leave the shell:

```bash
exit
```

Outside the dev shell, `jupyter` doesn't need to exist at all. The dependency stays with the project and never becomes permanent state on your machine.

## Running a command without entering a shell

An interactive shell is handy while you're developing, but Nix can also run a command directly:

```bash
nix develop --command jupyter lab
```

I find this useful in scripts, docs or editor config, because the command explicitly runs inside the flake's environment.

You can check the Python version the same way:

```bash
nix develop --command python --version
```

Or run an analysis script that's checked into the repo:

```bash
nix develop --command python analysis.py
```

With these commands you assume less about whatever shell the caller happens to be in.

## Loading the environment automatically

If you switch between projects a lot, it's easy to forget to type `nix develop` each time. `direnv` can load and unload environments for you when you enter or leave a directory.

Install `direnv` whichever way you usually install things on your workstation, turn on its shell integration, and create `.envrc` in the project:

```bash
use flake
```

Then allow it:

```bash
direnv allow
```

From then on, going into the directory loads the flake environment, and leaving it puts your old shell environment back.

Commit `.envrc` so your collaborators get the same behavior:

```bash
git add .envrc
git commit -m "Load development shell with direnv"
```

The allow step stays local, though. A checked-in `.envrc` isn't trusted automatically on another machine, which stops a repo from quietly running shell instructions you just downloaded.

## Adding more dependencies

Say the notebook needs SciPy and Seaborn later on. Add them to the Python package list:

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

Leave the dev shell and come back in, or reload `direnv`. Nix builds a new environment with the bigger package set. It doesn't change the old environment in place.

System tools go in the shell's `packages` list. For example, a notebook that converts documents or processes images might need Pandoc and ImageMagick:

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

To me this is one of the big advantages over a dependency file that only covers Python. The repo can declare the executables it needs right next to the Python libraries.

## Checking the flake

Before you share your changes, check the flake:

```bash
nix flake check
```

You can also look at its outputs:

```bash
nix flake show
```

The output should include a default development shell for your system.

For a small notebook repo, a useful `.gitignore` might have:

```gitignore
.direnv/
.ipynb_checkpoints/
__pycache__/
```

Don't ignore `flake.lock`. It's part of what makes the setup reproducible, and it should normally be committed.

## Where this stops helping

Nix makes the environment reproducible, but it can't promise that every notebook result comes out the same. An analysis can also depend on:

- Input datasets
- Random seeds
- Network services
- Numerical behavior that's specific to the hardware
- The order cells were run in the notebook
- Outside credentials or secrets

So versioning your data and running notebooks in a repeatable way still matter. Record your random seeds, don't rely on hidden notebook state, and write down where outside data comes from.

Don't put secrets in `flake.nix`, `flake.lock`, `.envrc` or the notebook. Pass them in at runtime through a proper secrets manager.

It's also worth checking whether a package is available in Nix before you mix Nix-managed Python packages with `pip install`. Installing one-off packages into the environment works against the declarative model, and it can break when native extensions expect libraries in the usual filesystem locations. When you can, declare dependencies in the flake so every workstation takes the same path.

## Conclusion

A Jupyter notebook is more useful when the environment it runs in travels with it. With a Nix flake, the repo defines the Python interpreter, the notebook server, the libraries and the other workstation tools in one place.

Day to day, there isn't much to it:

```bash
git clone <repository>
cd <repository>
nix develop
jupyter lab
```

And the committed lock file makes sure collaborators and future machines resolve the same package set revision.

For me that's the main benefit of managing a workstation with Nix. Install steps turn into config you can run, upgrades turn into changes you can review, and your project's tools stop depending on the accidental history of one particular machine.
