# Workstation management with Nix flakes: a Jupyter notebook example

Getting a Jupyter notebook to run somewhere else is rarely as simple as copying the `.ipynb` file.

The notebook might need a particular Python version, some native libraries or command-line tools, or package versions somebody installed months ago. A collaborator opens it on another machine and finds a module missing. Or a newer version of a dependency gives different results.

Nix flakes let you describe the whole development environment as code. So we don't write down a long list of install steps; we commit a small config file, and every workstation gets the same Python and Jupyter environment from it.

We'll build a reproducible Jupyter Lab environment with Python, NumPy, pandas, Matplotlib and ipykernel.

## Why Nix and not just pip

Most Python projects manage dependencies with `venv`, `pip`, Poetry or Conda. Those are fine, but they all assume you already have a compatible Python interpreter and the system libraries it needs.

Nix sits a level below that. It can manage the Python interpreter itself as well as the Python packages and Jupyter Lab, plus native libraries, command-line programs, environment variables and the versions of whatever tools the project uses.

A flake gives that environment a defined entry point and records its upstream inputs in a lock file. You can check the project out on any other machine that has Nix and get into the environment with one command. Nothing gets installed globally, either. Each repository has its own environment and the rest of the workstation is left alone.

## Setup

You need Nix installed with flakes turned on. Recent installs often turn flakes on in their config already. If yours doesn't, add this to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

After you change it, restart the Nix daemon if one is running, and any open terminals.

Check that it works:

```bash
nix --version
```

Make a directory for the example:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
git init
```

Flakes generally only see files that Git tracks, so we'll add the config to Git once it exists.

## The flake

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

The first run can take a while, because Nix has to fetch metadata and build or download the packages. After that it's usually much faster, since everything is already in the local Nix store.

The shell hook should print the Python version and remind you how to start Jupyter.

### What the file does

`inputs` lists the outside sources the flake uses:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
};
```

`nixpkgs` is the package collection that Python, Jupyter, Git and the Python libraries come from. `nixos-unstable` is a moving branch, but the flake locks it to one revision.

`flake-utils` helps build outputs for several common platforms. So the same file can give you a development shell on x86-64 Linux, ARM Linux or macOS, as long as the packages exist there.

In `outputs`, the chosen `nixpkgs` revision is imported for the current platform:

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

That gives you one Python interpreter with the listed packages on its import path. There's no separate `pip install` step, and nothing gets installed into your home directory.

Last, `pkgs.mkShell` defines what you get when you run `nix develop`: our Python and Git. You can add other non-Python tools to the `packages` list later.

## The lock file

That first `nix develop` also created `flake.lock`. Take a look:

```bash
git status
```

You should see both `flake.nix` and `flake.lock`. Commit them together:

```bash
git add flake.nix flake.lock
git commit -m "Add reproducible Jupyter environment"
```

`flake.nix` says which inputs the project wants. `flake.lock` records the exact revisions that were picked for them.

That difference matters. If all you had was a reference to `nixos-unstable`, two developers who entered the project at different times could get different package sets. With the lock file committed, both machines resolve the same `nixpkgs` revision.

When you do want to update the locked inputs, run:

```bash
nix flake update
```

Then look over and test the changes before you commit the new lock file. That way a dependency upgrade shows up as a change in the repository, and not as some invisible difference between two machines.

## Running Jupyter Lab

Get into the development shell if you aren't in it already:

```bash
nix develop
```

Start the server:

```bash
jupyter lab
```

Jupyter prints a local URL, usually with an auth token in it. Open it in a browser and create a Python notebook. Then try a small example:

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

The kernel starts from the environment Nix gave you, so the imports just work. You don't install anything from inside Jupyter.

When you're done, stop Jupyter and leave the shell:

```bash
exit
```

Outside the shell, `jupyter` doesn't have to exist at all. It belongs to the project and doesn't stick around on the workstation.

You don't have to enter the shell, either. Nix can run a command in the environment directly:

```bash
nix develop --command jupyter lab
```

That's handy in scripts, docs or editor config, because the command is explicitly run inside the flake's environment and doesn't depend on whatever shell the caller happens to be in. You can check the Python version the same way:

```bash
nix develop --command python --version
```

Or run an analysis script from the repository:

```bash
nix develop --command python analysis.py
```

## Loading it automatically with direnv

If you switch between projects a lot, it's easy to forget to type `nix develop`. `direnv` can load and unload the environment for you when you enter or leave a directory.

Install `direnv` however you normally install tools on your machine and turn on its shell integration. Then create `.envrc` in the project:

```bash
use flake
```

And allow it:

```bash
direnv allow
```

From then on, going into the directory loads the flake environment, and leaving it puts your old shell environment back.

Commit `.envrc` so collaborators get the same thing:

```bash
git add .envrc
git commit -m "Load development shell with direnv"
```

The `direnv allow` part stays local, though. A committed `.envrc` isn't trusted automatically on another machine, so a repository you just pulled can't quietly run shell commands on you.

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

Leave the shell and come back in, or reload `direnv`. Nix builds a new environment with the bigger package set. The old one isn't changed in place.

System tools go in the shell's `packages` list. A notebook that converts documents or processes images might need Pandoc and ImageMagick, for example:

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

This is one of the big advantages over a Python-only dependency file. The repository can declare the programs it needs right next to the Python libraries.

Before you share changes, check the flake:

```bash
nix flake check
```

You can also look at its outputs:

```bash
nix flake show
```

You should see a default development shell for your system in there.

For a small notebook repository, a `.gitignore` like this works:

```gitignore
.direnv/
.ipynb_checkpoints/
__pycache__/
```

Don't ignore `flake.lock`. It's a big part of why this is reproducible, and you should normally commit it.

## What Nix won't fix

Nix makes the environment reproducible. It can't promise that every notebook gives the same result, because an analysis can also depend on the input data, random seeds, network services, numerical behavior that's specific to the hardware, the order cells were run in, and outside credentials or secrets.

So versioning your data and running notebooks in a deterministic way still matter. Record the random seeds, don't rely on hidden notebook state, and write down where the outside data comes from.

Don't put secrets in `flake.nix`, `flake.lock`, `.envrc` or the notebook. Pass them in at runtime with a proper secret manager.

And check whether a package exists in Nix before you start mixing Nix-managed Python packages with `pip install`. Installing packages ad hoc into the environment works against the declarative setup, and it can fail when native extensions expect libraries in the usual filesystem locations. Where you can, declare the dependency in the flake so every workstation gets it the same way.

## Day to day

Once it's set up, the day-to-day part is short:

```bash
git clone <repository>
cd <repository>
nix develop
jupyter lab
```

And because the lock file is committed, your collaborators resolve the same package set you do, and so does any machine you set up later.