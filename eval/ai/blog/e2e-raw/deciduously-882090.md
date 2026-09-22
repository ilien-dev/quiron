# Workstation Management With Nix Flakes: Jupyter Notebook Example

Reproducing a Jupyter notebook is rarely as simple as copying the `.ipynb` file.

The notebook may depend on a particular Python version, native libraries, command-line utilities, or package versions installed months ago. A collaborator opens it on another workstation and discovers that a module is missing—or that a newer dependency produces different results.

Nix flakes provide a practical way to describe the entire development environment as code. Instead of documenting a long list of installation steps, we can commit a small configuration that gives every workstation the same Python and Jupyter environment.

In this tutorial, we will build a reproducible Jupyter Lab environment with Python, NumPy, pandas, Matplotlib, and ipykernel.

## What Nix adds to the workflow

Traditional Python projects usually manage dependencies with `venv`, `pip`, Poetry, or Conda. These tools are useful, but they generally begin after a compatible Python interpreter and required system libraries are already present.

Nix works at a lower level. It can manage:

- The Python interpreter
- Python packages
- Jupyter Lab
- Native libraries and command-line programs
- Environment variables
- Tool versions used by the project

A flake gives this environment a defined entry point and records its upstream inputs in a lock file. The result is a project that can be checked out on another Nix-enabled workstation and entered with one command.

This does not require installing the project’s tools globally. Each repository can have its own environment without changing the rest of the workstation.

## Prerequisites

You need Nix installed with flakes enabled. Recent Nix installations commonly enable flakes through configuration, but if necessary, add the following to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

Restart any active Nix daemon or terminal sessions after changing the configuration.

Verify the installation:

```bash
nix --version
```

Create a directory for the example:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
git init
```

Flakes generally operate on files tracked by Git. We will add the configuration after creating it.

## Creating the flake

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

The first invocation may take some time because Nix must fetch metadata and build or download the required packages. Later invocations are normally much faster because those artifacts are stored in the local Nix store.

The shell hook should display the Python version and remind you how to start Jupyter.

## Understanding the configuration

The `inputs` section declares external sources used by the flake:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
};
```

`nixpkgs` is the package collection from which Python, Jupyter, Git, and the Python libraries are obtained. The name `nixos-unstable` describes a moving branch, but the flake will lock it to a specific revision.

`flake-utils` helps produce outputs for several common platforms. The same configuration can therefore expose a development shell for systems such as x86-64 Linux, ARM Linux, and macOS, subject to package availability.

Inside `outputs`, the selected `nixpkgs` revision is imported for the current platform:

```nix
pkgs = import nixpkgs {
  inherit system;
};
```

The Python environment is then created with `withPackages`:

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

This produces one Python interpreter whose import path includes the listed packages. There is no separate `pip install` step and no dependency installation into the user’s home directory.

Finally, `pkgs.mkShell` defines what appears when we run `nix develop`. The environment contains our configured Python distribution and Git. Additional non-Python tools can be added to the `packages` list later.

## Locking the environment

The first `nix develop` command creates `flake.lock`. Inspect the repository:

```bash
git status
```

You should see both `flake.nix` and `flake.lock`. Commit them together:

```bash
git add flake.nix flake.lock
git commit -m "Add reproducible Jupyter environment"
```

`flake.nix` describes what inputs the project wants. `flake.lock` records the exact revisions selected for those inputs.

This distinction is important. Referencing `nixos-unstable` alone would otherwise mean that two developers entering the project at different times could receive different package sets. With the lock file committed, both workstations resolve the same `nixpkgs` revision.

To update the locked inputs intentionally, run:

```bash
nix flake update
```

Afterward, inspect and test the changes before committing the updated lock file. Dependency upgrades become visible repository changes instead of an invisible difference between machines.

## Running Jupyter Lab

Enter the development shell if you are not already inside it:

```bash
nix develop
```

Start the server:

```bash
jupyter lab
```

Jupyter will print a local URL, usually containing an authentication token. Open that URL in a browser and create a Python notebook.

Test the environment with a small example:

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

The notebook kernel is launched from the Nix-provided environment, so the imports are available without installing anything from the Jupyter interface.

When finished, stop Jupyter and leave the shell:

```bash
exit
```

Outside the development shell, `jupyter` does not need to be available at all. The dependency remains associated with the project rather than becoming permanent workstation state.

## Running a command without entering a shell

Interactive shells are convenient during development, but Nix can also execute commands directly:

```bash
nix develop --command jupyter lab
```

This is useful in scripts, documentation, or editor configuration because the command explicitly runs inside the flake’s environment.

You can verify the Python version in the same way:

```bash
nix develop --command python --version
```

Or execute a checked-in analysis script:

```bash
nix develop --command python analysis.py
```

These commands reduce assumptions about the caller’s current shell.

## Automatically loading the environment

If you frequently switch between projects, typing `nix develop` each time can become easy to forget. `direnv` can automatically load and unload environments when you enter or leave a directory.

Install `direnv` using your preferred workstation-level method, enable its shell integration, and create `.envrc` in the project:

```bash
use flake
```

Then authorize it:

```bash
direnv allow
```

From that point onward, entering the directory loads the flake environment. Leaving the directory restores the previous shell environment.

Commit `.envrc` so collaborators can use the same behavior:

```bash
git add .envrc
git commit -m "Load development shell with direnv"
```

Authorization remains local. A checked-in `.envrc` is not automatically trusted on another machine, which prevents repositories from silently executing newly downloaded shell instructions.

## Adding more dependencies

Suppose the notebook later needs SciPy and Seaborn. Add them to the Python package list:

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

Leave and re-enter the development shell, or reload `direnv`. Nix creates a new environment containing the expanded package set. It does not mutate the old environment in place.

System tools belong in the shell’s `packages` list. For example, a notebook that converts documents or processes images might need Pandoc and ImageMagick:

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

This is one of the main advantages over a Python-only dependency file: the repository can declare supporting executables alongside Python libraries.

## Checking the flake

Before sharing changes, validate the flake:

```bash
nix flake check
```

You can also inspect its outputs:

```bash
nix flake show
```

The output should include a default development shell for your system.

For a small notebook repository, a useful `.gitignore` might contain:

```gitignore
.direnv/
.ipynb_checkpoints/
__pycache__/
```

Do not ignore `flake.lock`; it is part of the reproducibility story and should normally be committed.

## A few practical boundaries

Nix improves environmental reproducibility, but it cannot guarantee that every notebook result is identical. Analyses may also depend on:

- Input datasets
- Random seeds
- Network services
- Hardware-specific numerical behavior
- Execution order within the notebook
- External credentials or secrets

Data versioning and deterministic notebook practices still matter. Record random seeds, avoid relying on hidden notebook state, and document how external data is obtained.

Secrets should not be written into `flake.nix`, `flake.lock`, `.envrc`, or the notebook. Provide them at runtime through an appropriate secret-management mechanism.

It is also worth checking package availability before mixing Nix-managed Python packages with `pip install`. Installing ad hoc packages into the environment undermines the declarative model and may fail when native extensions expect libraries in conventional filesystem locations. When possible, declare dependencies in the flake so every workstation follows the same path.

## Conclusion

A Jupyter notebook is more useful when its execution environment travels with it. With a Nix flake, the repository defines the Python interpreter, notebook server, libraries, and supporting workstation tools in one place.

The daily workflow remains small:

```bash
git clone <repository>
cd <repository>
nix develop
jupyter lab
```

Meanwhile, the committed lock file ensures that collaborators and future workstations resolve the same package-set revision.

That is the central benefit of workstation management with Nix: installation instructions become executable configuration, upgrades become reviewable changes, and project tools stop depending on the accidental history of a particular machine.