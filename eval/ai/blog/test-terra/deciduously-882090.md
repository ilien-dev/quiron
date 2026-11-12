# Workstation Management With Nix Flakes: Jupyter Notebook Example

A notebook that runs perfectly on your laptop can be surprisingly difficult to run six months later. Maybe Python was upgraded. Maybe a package installed globally changed. Maybe a colleague has the notebook but not the list of dependencies you installed along the way.

You can document the setup in a README, but documentation and workstations tend to drift apart. What if the project itself could describe the tools it needs?

Nix flakes give us a way to do that. In this post, we’ll create a project-specific Jupyter environment with Python, pandas, and matplotlib. We’ll also lock its dependencies so another workstation can use the same Nixpkgs revision.

By the end, starting the environment will look like this:

```bash
nix develop
jupyter notebook
```

The example uses a development shell, so you don’t need to run NixOS or replace your existing workstation configuration.

## What are Nix and flakes?

[Nix](https://nix.dev/) is a package manager that describes packages and environments as expressions. It stores software in the Nix store, allowing different versions of tools and libraries to coexist.

A **flake** is a standardized way to describe a Nix project. Its `flake.nix` file declares inputs, such as Nixpkgs, and outputs, such as packages or development shells. A companion `flake.lock` file records the exact revisions of those inputs.

For workstation management, this means we can put a project’s development tools under version control instead of relying on a sequence of manual installations. The [Nix flakes documentation](https://nix.dev/concepts/flakes.html) covers the format and notes that flakes remain an experimental Nix feature.

Our example will use:

- **Nixpkgs** as the source of Python and its packages.
- **A development shell** to make those tools available in a project directory.
- **A lock file** to keep the Nixpkgs revision consistent across machines.

This controls the software environment, but it doesn’t automatically freeze notebook data, random seeds, external APIs, or operating system behavior. We’ll come back to those limits.

## Prerequisites

Install Nix on a supported Linux or macOS machine using the [official installation instructions](https://nix.dev/install-nix.html). Windows users can follow along in a Linux environment such as WSL.

You’ll also need the `nix-command` and `flakes` experimental features enabled. One way to do that for an individual command is to add:

```bash
--extra-experimental-features 'nix-command flakes'
```

For example:

```bash
nix --extra-experimental-features 'nix-command flakes' --version
```

The commands below assume those features are already enabled in your Nix configuration. Consult the [flakes documentation](https://nix.dev/concepts/flakes.html) for configuration options.

## Create the project

Create a directory for the notebook project:

```bash
mkdir nix-jupyter-example
cd nix-jupyter-example
```

Add a file named `flake.nix`:

```nix
{
  description = "A reproducible Jupyter notebook environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
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
          pkgs = nixpkgs.legacyPackages.${system};

          python = pkgs.python3.withPackages (ps: with ps; [
            notebook
            ipykernel
            pandas
            matplotlib
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [ python ];

            shellHook = ''
              echo "Jupyter environment ready."
              echo "Start it with: jupyter notebook"
            '';
          };
        });
    };
}
```

Let’s unpack the important parts.

The `inputs` section points to the `nixos-unstable` branch of Nixpkgs. That branch changes over time, but the lock file will record the exact revision selected for this project.

The `systems` list tells the flake which platforms to expose development shells for. It does not guarantee every package works on every platform; package availability and support still depend on the chosen Nixpkgs revision.

Inside the shell, `python3.withPackages` creates a Python environment containing our selected packages:

- `notebook` provides the Jupyter Notebook interface.
- `ipykernel` lets Jupyter run Python code.
- `pandas` handles our example data.
- `matplotlib` creates a chart.

Finally, `pkgs.mkShell` defines the development environment. Its `packages` list puts our Python environment on the shell’s `PATH`. The `shellHook` prints a reminder whenever we enter it.

## Enter the development shell

From the project directory, run:

```bash
nix develop
```

On the first run, Nix resolves the flake input, creates `flake.lock`, and downloads or builds the required packages. This may take a little while.

Once you see the welcome message, check the available commands:

```bash
python --version
jupyter --version
```

You can also verify the Python imports:

```bash
python -c "import pandas, matplotlib, ipykernel; print('Imports work!')"
```

Now start Notebook:

```bash
jupyter notebook
```

Jupyter will print a local URL, typically including a token, and may open your browser automatically. If it doesn’t, copy the URL from the terminal into your browser. The [Jupyter installation guide](https://jupyter.org/install) also documents this launch command.

When you’re done, stop the server with `Ctrl+C` in its terminal. Exit the Nix development shell with:

```bash
exit
```

The packages remain in the Nix store for reuse, but they no longer need to be on your normal shell’s `PATH`.

## Create a notebook

In the Jupyter interface, create a new Python notebook. Add this code to a cell and run it:

```python
import pandas as pd
import matplotlib.pyplot as plt

data = pd.DataFrame(
    {
        "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "notebooks_run": [3, 5, 4, 7, 6],
    }
)

data
```

You should see a small table. Add a second cell:

```python
ax = data.plot.bar(
    x="day",
    y="notebooks_run",
    legend=False,
    color="steelblue",
    title="Notebooks run during the week",
)

ax.set_xlabel("")
ax.set_ylabel("Number of notebooks")
plt.tight_layout()
plt.show()
```

You now have a notebook whose Python dependencies are described in `flake.nix`.

To confirm which Python is executing the notebook, run another cell:

```python
import sys

print(sys.executable)
```

It should point to the Python environment supplied by Nix. If it points somewhere unexpected, check the selected kernel in Jupyter. A browser may connect to an already-running server, and a machine can have other kernels installed. Start the server from the project’s development shell and select its Python kernel.

## Commit the environment

Initialize a Git repository if you haven’t already:

```bash
git init
git add flake.nix flake.lock
git add *.ipynb
git commit -m "Add reproducible Jupyter environment"
```

The distinction between the two Nix files matters:

- `flake.nix` describes the input and the environment you want.
- `flake.lock` records the exact revision Nix resolved for that input.

Commit both. A teammate can then clone the repository, enter it, and run `nix develop` using the locked input. Without the lock file, the same branch reference could resolve to a newer Nixpkgs revision on another day. See the [Nix reference manual’s explanation of lock files](https://releases.nixos.org/nix/nix-2.35.1/manual/command-ref/new-cli/nix3-flake.html) for the details.

One Git detail can surprise new flake users: when a flake is inside a Git repository, Nix considers files known to Git when accessing the project as a Git flake. If you add a new Nix file that your flake imports, stage it with `git add` before evaluating the flake.

You may also want a `.gitignore` for local notebook checkpoints:

```gitignore
.ipynb_checkpoints/
```

Decide separately whether notebook outputs and datasets belong in your repository. Large datasets, credentials, and generated artifacts often need a different storage strategy.

## Add or update dependencies

Suppose the project needs NumPy explicitly. Add it to the Python package list:

```nix
python = pkgs.python3.withPackages (ps: with ps; [
  notebook
  ipykernel
  numpy
  pandas
  matplotlib
]);
```

Exit the existing shell and run `nix develop` again. Then verify the addition:

```bash
python -c "import numpy; print(numpy.__version__)"
```

Commit the `flake.nix` change so the rest of the team gets the same environment definition.

Updating Nixpkgs is a separate decision. To refresh the project’s locked inputs, run:

```bash
nix flake update
```

Then re-enter the shell and rerun the notebook before committing the changed `flake.lock`. An update can change Python and multiple library versions, so review it like any other dependency upgrade. The [Nix manual](https://releases.nixos.org/nix/nix-2.34.7/manual/command-ref/new-cli/nix3-flake-update.html) describes how to update all inputs or select a specific one.

If an update breaks your project, Git gives you a straightforward way to inspect and restore the previous lock file. Test the restored environment before continuing.

## How this helps manage a workstation

This example manages one project’s tools, not an entire machine. That is still a useful workstation management pattern.

Imagine working on two notebooks: one is a new analysis, and the other is an older report that depends on an earlier Python package set. Each repository can have its own flake and lock file. Enter the appropriate directory, run `nix develop`, and use the environment defined by that project.

The benefits extend to onboarding and machine replacement. Instead of reconstructing an environment from memory, you keep its definition next to the notebook. You can review dependency changes in pull requests, and teammates have a common starting point.

There are practical limits. A locked input does not guarantee identical results across CPU architectures or operating systems. It also doesn’t capture data downloaded from a changing URL, credentials, GPU drivers, or the state of an external database. For stronger reproducibility, version or otherwise identify your data, record relevant configuration, and control sources of randomness in the notebook.

Nix can also manage more than project shells. You might later explore NixOS for system configuration or Home Manager for user-level tools and dotfiles. You don’t have to adopt either to benefit from this example: a flake in a repository is a useful first step.

The next time someone asks how to run your notebook, you can point them to a versioned environment alongside the analysis. That makes the setup easier to share, review, and revisit when the project is no longer fresh in your memory.
