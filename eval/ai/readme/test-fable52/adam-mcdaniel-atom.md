# atom

**Shell scripting that will knock your socks off.**

atom is a shell and scripting language for people who love the command line but are tired of fighting it. It keeps what makes shells great (terse commands, pipes, instant feedback) and drops the parts that make shell scripts fragile: silent failures, word splitting, stringly-typed everything, and syntax nobody remembers without searching for it.

```atom
let logs = glob("/var/log/*.log")

for file in logs {
    let errors = read(file) | lines | where { it.contains("ERROR") }
    if errors.len() > 0 {
        echo "{file}: {errors.len()} errors"
    }
}
```

No quoting gymnastics, no `"${array[@]}"`, no `set -euo pipefail`. It reads like what it does.

## Contents

- [Why atom?](#why-atom)
- [Installation](#installation)
- [A quick tour](#a-quick-tour)
- [Using atom interactively](#using-atom-interactively)
- [Configuration](#configuration)
- [Coming from bash](#coming-from-bash)
- [Project status](#project-status)
- [Contributing](#contributing)
- [License](#license)

## Why atom?

Traditional shells were designed for typing commands, and scripting was added afterwards. That shows up the moment a script grows past twenty lines:

- **Errors are ignored by default.** A failed command in the middle of a script lets the rest carry on.
- **Everything is a string.** Numbers, lists, and paths all get re-parsed at every step, and a filename with a space can break the lot.
- **The syntax is full of traps.** `[ ]` versus `[[ ]]`, `$*` versus `$@`, and whether `=` tolerates spaces are all things you have to memorize.

atom starts from the other end. It is a small, real programming language whose most convenient operation happens to be running programs.

| | bash | atom |
|---|---|---|
| Failed command | Keeps going | Stops, with a trace |
| Variables with spaces | Split unless quoted | Never split |
| Data types | Strings | Strings, numbers, booleans, lists, maps |
| Functions | Positional `$1`, `$2` | Named parameters, return values |
| Reading JSON | Pipe to an external tool | Built in |

## Installation

### From a release

Download the binary for your platform from the releases page and put it somewhere on your `PATH`:

```sh
chmod +x atom
mv atom /usr/local/bin/
```

### From source

```sh
git clone https://github.com/<your-org>/atom.git
cd atom
make install
```

### Check that it works

```sh
atom --version
atom -c 'echo "hello from atom"'
```

To run a script, either pass it to `atom` or give it a shebang:

```atom
#!/usr/bin/env atom
echo "it works"
```

## A quick tour

### Variables are values, not text substitutions

```atom
let name = "My Documents"
mkdir name          # creates one directory, not two
cd name
```

A variable is always passed as exactly one argument. If you want a list to spread across arguments, say so:

```atom
let flags = ["-l", "-a", "-h"]
ls ...flags
```

Variables are immutable unless declared with `let mut`.

### Real data types

```atom
let port = 8080
let hosts = ["alpha", "beta", "gamma"]
let config = { name: "api", port: port, debug: false }

echo "Serving {config.name} on port {config.port + 1}"
echo "First host: {hosts[0]}, total: {hosts.len()}"
```

String interpolation uses `{}` and accepts any expression. Single-quoted strings are always literal.

### Running commands

Any line that isn't a keyword is a command, just as you would expect:

```atom
git status
docker build -t myapp .
```

Capture output with `$( )`. You get a string with the trailing newline removed, and nothing is split behind your back:

```atom
let branch = $(git branch --show-current)
let files = $(git diff --name-only) | lines
```

### Pipelines that carry structure

Pipes work between external programs exactly as they always have. Between atom functions, they carry values instead of bytes:

```atom
ps
    | where { it.cpu > 50 }
    | sort_by { it.mem }
    | take 5
    | each { echo "{it.pid}  {it.name}" }
```

Structured formats are first-class:

```atom
let pkg = read("package.json") | from_json
echo "Building {pkg.name} v{pkg.version}"

pkg.scripts | keys | each { echo " - {it}" }
```

`from_json`, `from_yaml`, `from_csv`, and `from_toml` are built in, along with their `to_*` counterparts.

### Errors stop the script

If a command exits non-zero, the script halts and tells you where:

```
error: command failed with exit code 1
  --> deploy.atom:14
   |
14 |     npm run build
   |     ^^^^^^^^^^^^^
```

When failure is expected, handle it explicitly:

```atom
try {
    curl --fail "https://example.com/health"
} catch err {
    echo "health check failed: {err.code}"
    exit 1
}
```

Or just ask whether something succeeded:

```atom
if ok { which docker } {
    echo "docker is installed"
}
```

### Functions with actual signatures

```atom
fn deploy(env, tag = "latest", dry_run = false) {
    if dry_run {
        echo "would deploy {tag} to {env}"
        return
    }
    kubectl set image "deploy/app" "app=registry/app:{tag}" -n env
}

deploy "staging"
deploy "production" --tag "v2.1.0" --dry-run
```

Named parameters automatically become flags, and `atom deploy.atom --help` generates usage text from your function signatures and doc comments.

### Modules

```atom
use "./lib/docker.atom"
use "./lib/notify.atom" as n

docker.build "myapp"
n.slack "build finished"
```

A module is just a file. Everything marked `pub` is exported.

### Parallelism without the pain

```atom
let servers = ["web1", "web2", "web3", "web4"]

let results = servers | par_each { |s|
    { host: s, uptime: $(ssh s uptime) }
}

results | each { echo "{it.host}: {it.uptime}" }
```

`par_each` runs the block concurrently, collects the results in order, and propagates the first failure. There are no background jobs or `wait` calls to manage, and output from different jobs is not interleaved.

## Using atom interactively

atom is a comfortable daily shell as well as a script runner:

- **Syntax highlighting** as you type, with errors flagged before you press Enter.
- **Autosuggestions** from history, accepted with the right arrow.
- **Completion** for commands, paths, flags, and git branches.
- **Multiline editing** that understands blocks, so pasting a function just works.
- **Searchable history** with `Ctrl-R`, shared across sessions.

To make atom your login shell:

```sh
echo "$(which atom)" | sudo tee -a /etc/shells
chsh -s "$(which atom)"
```

## Configuration

atom reads `~/.config/atom/config.atom` at startup. It is an ordinary atom script:

```atom
# Environment
env.EDITOR = "nvim"
env.PATH = ["~/.local/bin", ...env.PATH]

# Aliases
alias g = git
alias ll = ls -lah

# Prompt
fn prompt() {
    let branch = if ok { git rev-parse --git-dir } { " ({$(git branch --show-current)})" } else { "" }
    return "{cwd().short()}{branch} › "
}
```

`env.PATH` is a list. You append to it like a list, and atom joins it for child processes.

## Coming from bash

Most everyday commands work unchanged. These are the differences you will hit first:

| bash | atom |
|---|---|
| `x=5` | `let x = 5` |
| `"$x"` | `x`, or `"{x}"` inside strings |
| `$(cmd)` | `$(cmd)` |
| `if [ -f "$f" ]; then … fi` | `if exists(f) { … }` |
| `for f in *.txt; do … done` | `for f in glob("*.txt") { … }` |
| `cmd \|\| true` | `try { cmd }` |
| `cmd &` … `wait` | `spawn { cmd }` or `par_each` |
| `export FOO=bar` | `env.FOO = "bar"` |

atom is **not** POSIX-compatible and does not try to be. Existing scripts still run through `sh` or `bash`, and you can call them from atom like any other program. To convert a script gradually, `atom fmt --from-bash script.sh` produces a best-effort translation to start from.

## Project status

atom is under active development. The core language is stable enough for daily use, but details may change before 1.0. Breaking changes are recorded in the changelog.

On the roadmap:

- [ ] Native Windows support
- [ ] Language server for editor integration
- [ ] Package manager for sharing modules
- [ ] Debugger with breakpoints and stepping

## Contributing

Contributions of all sizes are welcome, including bug reports, documentation fixes, new built-ins, and ideas.

1. Open an issue to discuss anything larger than a small fix.
2. Fork the repository and create a branch.
3. Run `make test` and `make lint` before submitting.
4. Open a pull request describing what changed and why.

If you are not sure where to start, look for issues labeled `good first issue`. Please read the code of conduct before participating.

## License

atom is released under the MIT License. See [LICENSE](LICENSE) for details.

---

I only had the name and tagline to work from, so the syntax, built-ins, install steps, roadmap, and MIT license are invented placeholders. Replace them with what atom really does, and fill in `<your-org>` in the clone URL.
