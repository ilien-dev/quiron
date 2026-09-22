# Workstation management with Nix flakes: a Jupyter notebook example

Getting a Jupyter notebook to run the same way somewhere else is rarely as simple as copying the `.ipynb` file.

The notebook might depend on a particular Python version or on native libraries and command-line tools, or on package versions somebody installed months ago. A collaborator opens it on another machine and finds a module is missing. Or worse, a newer version of some dependency gives different results.

Nix flakes let you describe the whole development environment as code. So instead of writing down a long list of install steps, we can commit a small config file that gives every machine the same Python and Jupyter setup. The one we'll build here is a Jupyter Lab environment with Python, NumPy, pandas, Matplotlib and ipykernel.

## What Nix adds to the workflow

Most Python projects handle dependencies with `venv`, `pip`, Poetry or Conda. Those tools are fine, but they all assume you already have a Python that works and the system libraries it needs.

Nix works a level below that. It can manage:

- The Python interpreter
- Python packages
- Jupyter Lab
- Native libraries and command-line programs
- Environment variables
- Tool versions used by the project

A flake gives all of this one entry point and pins its upstream inputs in a lock file. You can check the project out on any other machine that has Nix and get into the environment with one command.

None of the project's tools get installed globally, either. Each repo can have its own environment and the rest of the machine stays the way it was.

## Prerequisites

You need Nix with flakes turned on. Recent installs often turn them on already, but if yours doesn't, add this to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

After you change it, restart the Nix daemon if it's running, and any open terminals.

Check that it works:

```bash
nix --version
```

Make a folder for the example:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
git init
```

Flakes mostly only see files that Git is tracking, so we'll add the config to Git once it exists.

## Creating the flake

Create `flake.nix`:

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

Now step into the environment:

```bash
nix develop
```

The first run can take a while, because Nix has to fetch metadata and then build or download the packages. After that it's usually much faster, since everything is already sitting in the local Nix store.

The shell hook should print the Python version and remind you how to start Jupyter.

## What the config does

`inputs` lists the outside sources the flake pulls from:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
};
```

`nixpkgs` is the package collection. Python comes from there, and so do Jupyter, Git and the Python libraries. `nixos-unstable` is a branch that keeps moving, but the flake locks it to one specific revision.

`flake-utils` makes it easy to produce outputs for the common platforms, so the same config can give you a dev shell on x86-64 Linux, ARM Linux or macOS (as long as the packages exist there).

Inside `outputs`, we import that pinned `nixpkgs` revision for whatever platform we're on:

```nix
pkgs = import nixpkgs {
  inherit system;
};
```

Then `withPackages` builds the Python environment:

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

What you get is a single Python interpreter that can import every package in that list. There's no separate `pip install` step, and nothing gets installed into your home directory.

Last, `pkgs.mkShell` says what's there when we run `nix develop`: our Python and Git. Any other non-Python tools can go in the `packages` list later.

## Locking the environment

Running `nix develop` the first time also wrote a `flake.lock`. Take a look:

```bash
git status
```

You should see `flake.nix` and `flake.lock`. Commit both together:

```bash
git add flake.nix flake.lock
git commit -m "Add reproducible Jupyter environment"
```

`flake.nix` says which inputs the project wants, and `flake.lock` records the exact revision it picked for each one.

That matters. If all you had was the `nixos-unstable` reference, two people who entered the project at different times could end up with different packages. With the lock file committed, both machines get the same `nixpkgs` revision.

When you do want to update the pinned inputs, run:

```bash
nix flake update
```

Then look over what changed and test it before you commit the new lock file. That way a dependency upgrade shows up as a change in the repo, and not as some difference between two machines that nobody can see.

## Running Jupyter Lab

Get into the dev shell if you aren't in it already:

```bash
nix develop
```

Start the server:

```bash
jupyter lab
```

Jupyter prints a local URL, usually with an auth token on the end. Open it in a browser and make a new Python notebook.

Try a small example to test it:

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

The kernel starts from the Nix environment, so those imports just work. You don't install anything from inside Jupyter.

When you're done, stop Jupyter and leave the shell:

```bash
exit
```

Outside the dev shell, `jupyter` doesn't have to exist at all. It belongs to the project, and it never becomes a permanent part of your machine.

## Running a command without entering a shell

The interactive shell is handy while you work, but Nix can also run a command directly:

```bash
nix develop --command jupyter lab
```

That's useful in scripts or docs, or in your editor config, because the command always runs inside the flake's environment.

You can check the Python version the same way:

```bash
nix develop --command python --version
```

Or run an analysis script that's in the repo:

```bash
nix develop --command python analysis.py
```

These make fewer assumptions about whatever shell the caller happens to be in.

## Loading the environment on its own

If you jump between projects a lot, it's easy to forget to type `nix develop` each time. `direnv` can load and unload environments for you when you go into or out of a folder.

Install `direnv` however you like to install things on your machine, and hook it into your shell. Then create `.envrc` in the project:

```bash
use flake
```

Then allow it:

```bash
direnv allow
```

From then on, going into the folder loads the flake environment, and leaving it puts your old shell environment back.

Commit `.envrc` so your collaborators get the same thing:

```bash
git add .envrc
git commit -m "Load development shell with direnv"
```

The `direnv allow` part stays local. A committed `.envrc` isn't trusted on someone else's machine until they allow it too, so a repo can't quietly run shell code you just downloaded.

## Adding more dependencies

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

Leave the dev shell and come back in, or reload `direnv`. Nix builds a new environment with the bigger package set. It doesn't change the old one in place.

System tools go in the shell's `packages` list. A notebook that converts documents or works on images, for example, might need Pandoc and ImageMagick:

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

This is one of the big wins over a Python-only dependency file. The repo can list the other programs it needs right next to the Python libraries.

## Checking the flake

Before you share changes, check the flake:

```bash
nix flake check
```

You can also look at its outputs:

```bash
nix flake show
```

You should see a default dev shell for your system.

For a small notebook repo, a `.gitignore` like this works:

```gitignore
.direnv/
.ipynb_checkpoints/
__pycache__/
```

Don't ignore `flake.lock`, though. It's a big part of what makes this reproducible, and you'll normally want it committed.

## What Nix can't fix

Nix makes the environment reproducible. It can't promise that every notebook gives the same result every time, because an analysis can also depend on:

- Input datasets
- Random seeds
- Network services
- Hardware-specific numerical behavior
- Execution order within the notebook
- External credentials or secrets

So versioning your data and keeping notebooks deterministic still matter. Write down your random seeds, don't lean on hidden notebook state, and note where outside data comes from.

Keep secrets out of `flake.nix`, `flake.lock`, `.envrc` and the notebook. Pass them in at runtime with whatever secret management you use.

And before you mix Nix-managed Python packages with `pip install`, check whether the package is already in Nix. Installing things ad hoc into the environment breaks the declarative model, and it can fail when native extensions look for libraries in the usual filesystem locations. Where you can, put dependencies in the flake so every machine gets them the same way.

## Day to day

Once this is set up, a new machine only needs:

```bash
git clone <repository>
cd <repository>
nix develop
jupyter lab
```

The committed lock file means your collaborators, and any machine you set up later, get the same package revisions you have. Install instructions turn into config that actually runs, and an upgrade is a diff someone can review. The tools stop depending on whatever happened to get installed on one particular machine.