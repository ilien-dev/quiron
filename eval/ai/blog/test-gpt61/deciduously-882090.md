# Workstation Management With Nix Flakes: Jupyter Notebook Example

A notebook is easy to share. The environment that runs it is harder.

You send someone an `.ipynb` file, and they immediately encounter a missing dependency. They install it, discover a Python version mismatch, create another virtual environment, and eventually get the notebook running—with slightly different results.

The same problem appears when rebuilding your own workstation. Your files are backed up, but your development environment lives partly in configuration files and partly in memory.

Nix offers a way to describe that environment as code. With flakes, you can keep its definition and dependency revisions beside your notebooks.

Let’s build a Jupyter Notebook environment with Python, pandas, NumPy, and Matplotlib, then look at how this approach fits into workstation management.

## Why manage a development environment with Nix?

A workstation usually supports several projects, each with different requirements. One needs a particular Python ecosystem. Another needs Node.js, a database client, and a compiler.

Installing everything globally makes those requirements difficult to separate.

With Nix, a project can declare its own tools. Enter its development shell, and those tools become available. Leave the shell, and your ordinary terminal environment takes over again.

For a notebook project, that means tracking more than a list of Python libraries. We can describe the interpreter, Jupyter, and supporting command-line tools together.

This gives us a useful division of responsibility: the workstation provides Nix, while each repository describes the environment needed to work on it.

## What a flake adds

A flake is a directory containing a `flake.nix` file. That file declares **inputs**, such as Nixpkgs, and **outputs**, such as development shells or packages.

A companion `flake.lock` records the resolved revisions of those inputs. A moving reference such as `nixpkgs-unstable` selects an initial source; the lock file records the particular revision used afterward.

Both files belong in version control. Together, they make environment changes reviewable alongside application changes. The [Nix flake reference](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake) explains this structure in more detail.

For this example, our output will be a development shell named `default`.

## Prepare the project

You’ll need Nix installed on Linux or macOS. On Windows, follow this example inside a Linux distribution running under WSL2.

If your installation hasn’t enabled flakes and the modern command interface, add this to `~/.config/nix/nix.conf`:

```ini
experimental-features = nix-command flakes
```

These interfaces are still marked experimental in the [Nix documentation](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake).

Create a project directory:

```bash
mkdir notebook-workstation
cd notebook-workstation
git init
mkdir notebooks
```

Now create `flake.nix`:

```nix
{
  description = "A reproducible Jupyter Notebook environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };

          pythonEnv = pkgs.python3.withPackages (ps: [
            ps.notebook
            ps.ipykernel
            ps.numpy
            ps.pandas
            ps.matplotlib
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              pythonEnv
              pkgs.git
            ];

            # Avoid importing packages from ~/.local.
            PYTHONNOUSERSITE = "1";

            shellHook = ''
              echo "Notebook environment ready."
              echo "Start with: python -m notebook notebooks"
            '';
          };
        });
    };
}
```

Stage the file before asking Nix to evaluate the Git-backed project:

```bash
git add flake.nix
nix flake lock
git add flake.lock
git commit -m "Define notebook development environment"
```

New, untracked files can be omitted from a Git-backed flake’s source snapshot. Staging `flake.nix` avoids a confusing “file not found” error.

## Understand the environment definition

The example contains a few ideas worth understanding before extending it.

First, `systems` lists the platform identifiers for which we expose development shells. This lets the same configuration describe environments for common Linux and macOS machines. Individual packages still need to support the selected platform.

Second, `python3.withPackages` constructs a Python environment containing the selected libraries. Jupyter and the scientific packages come from the same Python package set. This is a standard pattern documented in the [Nixpkgs Python guide](https://nixos.org/manual/nixpkgs/stable/#python).

Third, `mkShell` collects the tools we want available during development. We include Git to illustrate that the environment can contain ordinary command-line programs alongside Python.

Finally, the shell hook prints a reminder. It doesn’t launch a server automatically. Entering a shell should remain useful for editing files, inspecting dependencies, or running scripts.

## Launch Jupyter Notebook

Enter the environment:

```bash
nix develop
```

The first invocation may download a substantial collection of dependencies. Later invocations can reuse the local Nix store.

Inside the shell, start Jupyter:

```bash
python -m notebook notebooks
```

Using `python -m notebook` makes the selected Python interpreter explicit. Jupyter normally opens a browser and prints its connection URL in the terminal. See the [Jupyter launch documentation](https://docs.jupyter.org/en/latest/running.html) for the basic server workflow.

You can also launch it directly without first entering an interactive shell:

```bash
nix develop --command python -m notebook notebooks
```

The `--command` option runs a program within the development environment, as described in the [`nix develop` reference](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-develop).

Create a notebook and select the Python kernel associated with this environment.

## Verify the notebook’s interpreter

A running Jupyter server doesn’t necessarily mean your notebook uses the expected Python interpreter. Previously installed kernels can still appear in the interface.

Run this cell first:

```python
import sys

print(sys.executable)
```

For this setup, expect an interpreter path under `/nix/store/`. If it points to an old virtual environment, select the appropriate Python kernel and restart it.

Then try a small analysis:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

data = pd.DataFrame({
    "day": np.arange(1, 8),
    "requests": rng.integers(100, 300, size=7),
})

display(data)

data.plot(
    x="day",
    y="requests",
    kind="bar",
    legend=False,
)

plt.ylabel("Requests")
plt.title("Requests per day")
plt.tight_layout()
plt.show()
```

This checks that the interpreter can import the main libraries and render a chart. Save the notebook under `notebooks/`.

A fixed random seed helps make this example repeatable, though repeatable research also requires controlling data, execution order, and other inputs.

## Change dependencies deliberately

Suppose the analysis now needs SciPy. Add it to the package list:

```nix
pythonEnv = pkgs.python3.withPackages (ps: [
  ps.notebook
  ps.ipykernel
  ps.numpy
  ps.pandas
  ps.matplotlib
  ps.scipy
]);
```

Stop Jupyter, leave the shell, and enter again:

```bash
exit
nix develop
python -m notebook notebooks
```

Restart the notebook kernel before importing the new dependency.

For this workflow, declare persistent dependencies in `flake.nix`. Installing packages interactively with `pip` would introduce state that the flake doesn’t describe. Someone cloning the repository would then receive an incomplete environment.

Nixpkgs won’t contain every package or version you might need. Projects with more demanding Python requirements may need additional packaging work or an explicitly managed Python dependency workflow.

## Update and recover

Adding a package and updating Nixpkgs are separate operations. You can add a package while keeping the existing locked revision.

When you intentionally want newer packages, run:

```bash
nix flake update
```

Then launch the environment and rerun your notebooks. Review the lock-file change before committing it.

If the update causes a regression, restore the last known working `flake.nix` and `flake.lock` from Git, then launch the environment again. Keep those files together: a newer environment definition may reference packages unavailable in an older Nixpkgs revision.

This makes upgrades an explicit maintenance task with a recorded recovery path.

## Where this fits into workstation management

This project manages one working environment. It doesn’t configure your desktop, provision user accounts, or install system services.

That limited scope makes it a practical starting point. You can adopt project flakes on an existing workstation, then consider broader tools such as Home Manager or NixOS when you want to manage user configuration or the operating system.

There are also boundaries to remember. A development shell inherits parts of the host environment; it isn’t a container or a security sandbox. Notebook results can still depend on external datasets, credentials, hardware, and network services.

Keep a README explaining how to obtain data and run the analysis. Keep secrets outside the flake and repository.

The useful change is that rebuilding your workstation no longer requires remembering how you assembled this particular Python stack. Clone the repository, run `nix develop`, and start Jupyter. The environment has become part of the project—something you can inspect, share, update, and recover through version control.
