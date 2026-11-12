# Spearmint

Spearmint is a package to perform Bayesian optimization according to the algorithms outlined in the paper:

> **Practical Bayesian Optimization of Machine Learning Algorithms**
> Jasper Snoek, Hugo Larochelle and Ryan P. Adams
> *Advances in Neural Information Processing Systems*, 2012

The code is designed to run experiments automatically (hence the name "spearmint"), iteratively adjusting a set of parameters to minimize an objective in as few runs as possible. It is aimed at problems where each evaluation is expensive, such as training a machine learning model, and where grid search or random search would waste too many runs.

## How it works

Spearmint treats your objective as a black box. It places a Gaussian process (GP) prior over the function, updates that model with each observed result, and uses an acquisition function to decide which parameter setting to try next. Three ideas from the paper drive the implementation:

- **Integrated hyperparameters.** The GP's own hyperparameters are marginalized with slice sampling (MCMC) rather than fixed to a point estimate, so the search is far less sensitive to kernel settings.
- **Cost-aware search.** The expected improvement *per second* criterion models how long each evaluation takes and favors points that are both promising and cheap.
- **Parallel experiments.** When jobs are still running, Spearmint integrates over their possible outcomes, so new suggestions account for pending work instead of duplicating it.

## Contents

The repository contains two ways of running the same optimization machinery:

| Directory | Purpose |
|---|---|
| `spearmint/` | The full version. It launches jobs for you, locally or on a cluster, tracks their status, and can serve a status page. |
| `spearmint-lite/` | A stripped-down version. It only proposes the next experiments, and you run them and record the results yourself. |

Both come with example experiments, including the Branin test function used below.

## Dependencies

- Python 2.7
- [NumPy](http://www.numpy.org/) and [SciPy](http://www.scipy.org/)
- [Google Protocol Buffers](https://developers.google.com/protocol-buffers/), for the full version only (it is used for experiment configuration)

`spearmint-lite` needs only Python, NumPy and SciPy.

## Installation

Spearmint can be run straight from a checkout:

```bash
cd spearmint/bin
./make_protobufs
```

`make_protobufs` compiles the protocol buffer definitions and needs the `protoc` compiler on your path.

Alternatively, install the package and its `spearmint` command:

```bash
python setup.py install
```

## Running the full version

### 1. Write a wrapper for your objective

Spearmint calls a function named `main` in a module named after your experiment. It receives a job id and a dictionary of parameters, and returns the value to be **minimized**:

```python
# branin.py
import math

def branin(x, y):
    y_term = y - (5.1 / (4 * math.pi ** 2)) * x ** 2 + (5 / math.pi) * x - 6
    return y_term ** 2 + 10 * (1 - 1 / (8 * math.pi)) * math.cos(x) + 10

def main(job_id, params):
    # Each parameter arrives as an array, even when its size is 1.
    return branin(params['x'][0], params['y'][0])
```

To maximize a quantity such as validation accuracy, return its negative.

### 2. Describe the search space

Each experiment lives in its own directory with a `config.pb` file:

```
language: PYTHON
name:     "branin"

variable {
  name: "x"
  type: FLOAT
  size: 1
  min:  -5
  max:  10
}

variable {
  name: "y"
  type: FLOAT
  size: 1
  min:  0
  max:  15
}
```

- `language` says how the wrapper is invoked (for example `PYTHON` or `MATLAB`).
- `name` is the module or script containing your wrapper.
- Each `variable` has a `type` of `FLOAT`, `INT` or `ENUM`. Numeric types take `min` and `max`, and `ENUM` takes a list of `options`.
- `size` greater than 1 declares a vector-valued parameter.

### 3. Launch the optimization

```bash
cd spearmint/bin
./spearmint ../examples/braninpy/config.pb --driver=local --method=GPEIOptChooser --method-args=noiseless=1
```

Spearmint now proposes a point, runs the job, records the result, and repeats. Stop it at any time with Ctrl-C. State is kept in the experiment directory, so rerunning the same command resumes where it left off.

### Common options

| Option | Meaning |
|---|---|
| `--driver` | Where jobs run: `local` for this machine, `sge` for a Sun Grid Engine cluster. |
| `--method` | The chooser module that picks the next experiment (see below). |
| `--method-args` | Comma-separated arguments passed to the chooser, e.g. `noiseless=1`. |
| `--max-concurrent` | Maximum number of jobs to run at once. |
| `--max-finished-jobs` | Stop after this many jobs have completed. |
| `--grid-size` | Number of candidate points considered per variable set. |
| `--grid-seed` | Seed for the candidate grid, for reproducible runs. |
| `-w` | Start a small web server showing experiment status. |

Run `./spearmint --help` for the complete list.

### Results

Spearmint writes its output into the experiment directory:

- `output/` holds one log file per job, with whatever your code printed.
- `best_job_and_result.txt` records the best objective value so far and the parameters that produced it.
- `trace.csv` is a running history of the best value, along with the counts of pending and completed jobs.

To discard an experiment's state and start over:

```bash
./cleanup ../examples/braninpy
```

## Choosers

The `--method` option selects the acquisition strategy:

| Chooser | Description |
|---|---|
| `GPEIOptChooser` | GP with expected improvement, with candidates refined by numerical optimization of the acquisition function. A good default. |
| `GPEIperSecChooser` | Expected improvement per second. Use it when the running time varies a lot across the search space. |
| `GPEIChooser` | GP with expected improvement, evaluated on the candidate grid only. |
| `GPConstrainedEIChooser` | Expected improvement for objectives that can fail or violate constraints in parts of the space. |
| `RandomForestEIChooser` | Uses a random forest instead of a GP as the surrogate model. |
| `RandomChooser` | Uniform random search, useful as a baseline. |
| `SequentialChooser` | Walks through the candidate grid in order. |

Useful chooser arguments include `noiseless=1` for deterministic objectives, `mcmc_iters` to set the number of hyperparameter samples, and `burnin` to set how many samples are discarded at the start. If your objective is noisy, as most model training is, leave `noiseless` off.

## Running spearmint-lite

`spearmint-lite` suits setups where Spearmint cannot launch jobs itself, for instance when experiments are run by hand or by another scheduler. It reads a `config.json` describing the variables and a `results.dat` file in the experiment directory, and appends new suggestions to that file:

```bash
cd spearmint-lite
python spearmint-lite.py braninpy
```

Each line of `results.dat` is one experiment, in whitespace-separated columns:

```
<objective> <duration> <param 1> <param 2> ...
```

Proposed experiments are written with `P` in the first two columns to mark them as pending. Once you have run one, replace the `P` entries with the observed objective value and the running time, then call `spearmint-lite` again to get the next suggestion. Pending lines are taken into account, so you can request several experiments and run them in parallel:

```bash
python spearmint-lite.py --method=GPEIOptChooser --n-pending=4 braninpy
```

## Practical tips

- **Scale your variables sensibly.** Parameters that span orders of magnitude, such as learning rates, are best searched in log space. Declare the exponent as the variable and transform it in your wrapper.
- **Keep the dimension modest.** GP-based optimization works best on a handful to a few dozen parameters.
- **Handle failures.** If a setting can crash or diverge, return a large objective value or use the constrained chooser, so that one bad region does not stall the search.
- **Make the wrapper self-contained.** Jobs may run on different machines under the `sge` driver, so do not rely on local state.
- **Don't trust the first few runs.** Early suggestions are exploratory. The model needs several observations before its proposals become informed.

## Citing

If you use Spearmint in your research, please cite the paper:

```bibtex
@inproceedings{snoek2012practical,
  title     = {Practical Bayesian Optimization of Machine Learning Algorithms},
  author    = {Snoek, Jasper and Larochelle, Hugo and Adams, Ryan P.},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2012}
}
```

## License

Spearmint is distributed under the GNU General Public License, version 3. See the license file in the repository for the full terms.

---

I wrote this from memory of the original Spearmint codebase, so check the option names, output file names and license against the actual repository before publishing.
