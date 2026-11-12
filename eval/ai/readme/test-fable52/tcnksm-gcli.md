# gcli

The easy way to build Golang command-line application.

`gcli` generates the skeleton of a command-line application written in Go. You tell it the name of your tool, the commands it should have, and the CLI framework you prefer. It writes the boilerplate: the entry point, command stubs, flag parsing, tests, and the project files around them. The generated project builds with `go build` immediately, so you can start with the part that makes your tool yours.

## Contents

- [Why gcli](#why-gcli)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Usage](#usage)
- [The design file](#the-design-file)
- [Supported frameworks](#supported-frameworks)
- [What gets generated](#what-gets-generated)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Why gcli

Most Go CLI tools begin with the same hour of typing: a `main.go`, a version constant, flag definitions, a dispatch table, help text, exit codes, and a first round of tests. That code is rarely interesting, and it is easy to get subtly wrong.

`gcli` removes that hour:

- **One command to a working project.** The output compiles and its tests pass before you write a line.
- **Your choice of framework.** The same description of a tool can be generated for several popular CLI packages, or for the standard library alone.
- **Tests included.** Each generated command gets a test file, so testing is the default from the first commit.
- **Designs you can review.** A tool can be described in a small TOML file, validated, and then generated.
- **No runtime dependency.** `gcli` is a generator, not a library. The code it writes belongs to you and never imports `gcli`.

## Installation

With a Go toolchain installed:

```bash
go install github.com/tcnksm/gcli@latest
```

Make sure `$(go env GOPATH)/bin` is on your `PATH`.

On macOS you can use Homebrew:

```bash
brew tap tcnksm/gcli
brew install gcli
```

Prebuilt binaries for Linux, macOS, and Windows are attached to each release on GitHub. Download one, unpack it, and put it on your `PATH`.

Check the install:

```bash
gcli -version
```

## Quick start

Suppose you want a `todo` tool with three commands: `add`, `list`, and `delete`.

```bash
gcli new -F mitchellh_cli -c add -c list -c delete todo
```

`gcli` creates the project, prints each file it writes, and tells you where it put them. Then:

```bash
cd todo
go build
./todo help
```

You now have a binary with three subcommands, help output, a `-version` flag, and a test suite. Open `command/add.go`, find the `Run` function, and start writing real code.

## Usage

```
gcli [-version] [-help] <command> [options]
```

| Command    | Purpose                                            |
|------------|----------------------------------------------------|
| `new`      | Generate a new CLI project from command-line flags |
| `design`   | Generate a design template file                    |
| `validate` | Check a design file for errors                     |
| `apply`    | Generate a project from a design file              |
| `list`     | Show the available CLI frameworks                  |

Run `gcli help <command>` for the full option list of any command.

### `gcli new`

Generates a project directly from flags.
This is the fastest route when the tool is small.

```bash
gcli new [options] NAME
```

| Option               | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `-command`, `-c`     | Add a command. Repeat it for each one. Format: `NAME` or `NAME:"description"` |
| `-flag`, `-f`        | Add a global flag. Format: `NAME[:TYPE[:"description"]]`          |
| `-framework`, `-F`   | CLI framework to generate for. See `gcli list`                   |
| `-owner`, `-o`       | Owner used in the import path. Defaults to your git user name    |
| `-skip-test`, `-T`   | Skip the test run after generation                               |
| `-current`, `-C`     | Create the project in the current directory                      |

Example with descriptions:

```bash
gcli new -F urfave_cli \
  -c add:"Add a new task" \
  -c list:"List all tasks" \
  todo
```

A tool with no subcommands, only flags:

```bash
gcli new -F flag -f verbose:bool:"Print debug output" -f port:int grep-ish
```

### `gcli design`, `validate`, and `apply`

For anything beyond a handful of commands, flags on the command line get unwieldy.
The design workflow splits generation into three steps.

1. Create a template:

   ```bash
   gcli design -F mitchellh_cli todo
   ```

   This writes `todo-design.toml`.

2. Edit the file, then check it:

   ```bash
   gcli validate todo-design.toml
   ```

   Validation reports missing names, unknown frameworks, duplicate commands, and invalid flag types.

3. Generate the project:

   ```bash
   gcli apply todo-design.toml
   ```

The design file is plain text, so it can be committed, reviewed in a pull request, and reused to regenerate the skeleton later.

### `gcli list`

Prints the frameworks this version of `gcli` can generate for, with a link to each.

## The design file

A design file is TOML. A complete example:

```toml
name        = "todo"
owner       = "tcnksm"
version     = "0.1.0"
description = "Manage your tasks from the terminal"
framework   = "mitchellh_cli"

[[commands]]
name        = "add"
description = "Add a new task"

  [[commands.flags]]
  name        = "priority"
  type        = "int"
  description = "Priority of the task"

[[commands]]
name        = "list"
description = "List all tasks"

[[commands]]
name        = "delete"
description = "Delete a task"
```

| Field         | Required | Meaning                                              |
|---------------|----------|------------------------------------------------------|
| `name`        | yes      | Name of the binary and the project directory         |
| `owner`       | no       | Used to build the import path                        |
| `version`     | no       | Initial version string, default `0.1.0`              |
| `description` | no       | One-line summary shown in help output and the README |
| `framework`   | no       | One of the names shown by `gcli list`                |
| `commands`    | no       | Array of subcommands, each with optional `flags`     |

Supported flag types are `string`, `int`, and `bool`.

## Supported frameworks

| Name            | Package                    | Style                        |
|-----------------|----------------------------|------------------------------|
| `mitchellh_cli` | `github.com/mitchellh/cli` | Subcommands                  |
| `urfave_cli`    | `github.com/urfave/cli`    | Subcommands                  |
| `go_cmd`        | Standard library only      | Subcommands, like the `go` tool |
| `flag`          | Standard library `flag`    | Single command with flags    |

Pick a subcommand style if your tool has verbs (`todo add`, `todo list`).
Pick `flag` if it does one thing and is configured by options.
If you have no preference, `mitchellh_cli` is a sensible default.
It keeps each command in its own file behind a small interface, which makes commands easy to test.

## What gets generated

For the quick start example, the result looks like this:

```
todo/
├── main.go            # entry point, calls into cli.go
├── cli.go             # command registration and exit codes
├── version.go         # name and version constants
├── command/
│   ├── meta.go        # shared state for all commands
│   ├── add.go
│   ├── add_test.go
│   ├── list.go
│   ├── list_test.go
│   ├── delete.go
│   └── delete_test.go
├── README.md
├── CHANGELOG.md
└── .gitignore
```

The exact layout depends on the framework, because `gcli` follows each framework's conventions.
In every case you get:

- an entry point that returns proper exit codes,
- one stub per command with its help text and flags wired up,
- a test file per command,
- a README and a changelog to fill in.

After writing the files, `gcli` runs `go build` and `go test` in the new project to confirm the skeleton is sound.
Pass `-skip-test` to turn this off.

## FAQ

**Can I regenerate after editing the code?**
`gcli` is meant for starting a project. Running `apply` again writes a fresh skeleton and does not merge with your changes. Generate into a new directory and copy over what you need.

**Does my project depend on gcli afterwards?**
No. The only dependencies are those of the framework you chose, and `go_cmd` and `flag` have none.

**Where is the project created?**
In a directory named after the tool, under the current directory when `-current` is set, otherwise under `$GOPATH/src/github.com/<owner>/<name>`.

**Can I add my own framework?**
Yes. Frameworks are defined as sets of templates in the `skeleton` package. See below.

## Contributing

Bug reports, fixes, and new framework templates are welcome.

1. Fork the repository.
2. Create a branch for your change.
3. Run `go test ./...`. Changes to templates should also pass the integration tests, which generate a project for each framework and build it.
4. Open a pull request describing what changed and why.

For a new framework, add its templates under `skeleton/resource/tmpl/<name>/` and register it in the framework list. Open an issue first if the change is large.

## License

`gcli` is released under the [MIT License](LICENSE).
