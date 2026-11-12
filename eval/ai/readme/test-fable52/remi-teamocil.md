# Teamocil

> There's no I in Teamocil. At least not where you think.

Teamocil is a simple tool used to automatically create windows and panes in [tmux](https://github.com/tmux/tmux) with YAML files. Describe your layout once, then rebuild it with a single command whenever you need it.

## Installation

Teamocil is distributed as a Ruby gem. You need Ruby and a working tmux installation.

```bash
# Install the gem
gem install teamocil

# Create the directory that holds your layout files
mkdir ~/.teamocil

# Open a new layout file in your $EDITOR
teamocil --edit sample

# Launch tmux, then run your new layout
tmux
teamocil sample
```

Teamocil must be run from inside a tmux session, because it works by sending commands to the tmux server you are attached to.

## Usage

```bash
teamocil [options] <layout>
```

A layout name maps to a file in `~/.teamocil`. Running `teamocil sample` loads `~/.teamocil/sample.yml`.

### Global options

| Option    | Description                    |
|-----------|--------------------------------|
| `--list`  | Lists all available layouts in `~/.teamocil` |
| `--help`  | Prints the usage information |
| `--version` | Prints the installed version |

### Layout options

| Option      | Description                    |
|-------------|--------------------------------|
| `--layout [path]` | Uses the layout file at the given path instead of looking in `~/.teamocil` |
| `--here`    | Sets up the first window in the current tmux window instead of creating a new one |
| `--edit`    | Opens the layout file in `$EDITOR` |
| `--show`    | Prints the contents of the layout file instead of executing it |
| `--debug`   | Prints the tmux commands that would be run, without running them |

`--debug` is the fastest way to find out why a layout does not behave as expected: it shows exactly what Teamocil would send to tmux.

## Configuration

A layout file is a YAML document describing a session, its windows, and the panes inside each window.

### Session

| Key       | Description                    |
|-----------|--------------------------------|
| `name`    | The tmux session name. If set, the current session is renamed |
| `windows` | An array of window definitions |

### Windows

| Key       | Description                    |
|-----------|--------------------------------|
| `name`    | The tmux window name. **Required** |
| `root`    | The path where all panes in the window are started |
| `layout`  | The layout passed to tmux's `select-layout` command |
| `panes`   | An array of pane definitions |
| `focus`   | If `true`, this window is selected once the layout is built |
| `options` | A hash of tmux window options to set with `set-window-option` |

The `layout` value can be any of tmux's preset layouts (`even-horizontal`, `even-vertical`, `main-horizontal`, `main-vertical`, `tiled`) or a custom layout string as printed by `tmux list-windows`.

### Panes

A pane can be written either as a plain string, which is treated as a single command, or as a hash with these keys:

| Key        | Description                    |
|------------|--------------------------------|
| `commands` | An array of commands to run in the pane |
| `focus`    | If `true`, this pane is selected once the layout is built |

Commands in a pane are joined and sent to the shell in order, so later commands only make sense if the earlier ones return.

## Examples

### A simple two-pane window

```yaml
windows:
  - name: sample-two-panes
    root: ~/Code/sample/www
    layout: even-horizontal
    panes:
      - git status
      - rails server
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### A four-pane tiled window

```yaml
windows:
  - name: sample-four-panes
    root: ~/Code/sample/www
    layout: tiled
    panes:
      - git status
      - bundle exec rails server
      - bundle exec sidekiq
      - tail -f log/development.log
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|------------------|------------------|
| (2)              | (3)              |
|                  |                  |
'------------------'------------------'
```

### Multiple commands and a focused pane

```yaml
windows:
  - name: sample-focus
    root: ~/Code/sample/www
    layout: main-vertical
    panes:
      - commands:
          - git fetch
          - git status
        focus: true
      - rails server
      - rails console
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |------------------|
|                  | (2)              |
|                  |                  |
'------------------'------------------'
```

### Multiple windows with a named session

```yaml
name: my-project
windows:
  - name: editor
    root: ~/Code/my-project
    focus: true
    panes:
      - vim

  - name: servers
    root: ~/Code/my-project
    layout: even-vertical
    options:
      synchronize-panes: 'off'
    panes:
      - bin/server
      - bin/worker

  - name: logs
    root: ~/Code/my-project/log
    panes:
      - tail -f development.log
```

Each window is created in order, and the `editor` window is selected once everything is built.

## Extras

### Zsh autocompletion

Add this line to your `~/.zshrc` to complete layout names from `~/.teamocil`:

```zsh
compctl -g '~/.teamocil/*(:t:r)' teamocil
```

### Bash autocompletion

Add this line to your `~/.bashrc`:

```bash
complete -W "$(teamocil --list)" teamocil
```

### Per-project layouts

Layouts do not have to live in `~/.teamocil`. You can keep a layout file in a project's repository and share it with the rest of the team:

```bash
teamocil --layout ./.teamocil.yml
```

Combined with `--here`, this lets you open a terminal in a project directory and build the workspace in place without leaving a stray empty window behind.

## Troubleshooting

**Nothing happens, or I get an error about tmux.**
Check that you are running the command from inside a tmux session. Teamocil does not start tmux for you.

**My panes start in the wrong directory.**
Make sure `root` is set on the window and that the path exists. Paths starting with `~` are expanded by your shell.

**Commands run before my shell is ready.**
Heavy shell startup files can delay the prompt. Trimming the startup configuration, or moving slow initialization out of interactive startup, usually resolves this.

**Window or pane numbering is off.**
Teamocil reads the `base-index` and `pane-base-index` options from tmux. If you change them in `~/.tmux.conf`, reload the configuration before running a layout.

**I want to see what Teamocil is doing.**
Run the layout with `--debug` to print every tmux command without executing it.

## Contributing

Bug reports and pull requests are welcome.

1. Fork the repository.
2. Create a topic branch: `git checkout -b my-change`.
3. Make your changes and add specs covering them.
4. Run the test suite: `bundle exec rake spec`.
5. Open a pull request describing what changed and why.

Please keep changes focused. Teamocil is intentionally small, and features that can be handled by tmux itself or by a line of shell usually belong there.

## License

Teamocil is released under the MIT License. See the `LICENSE.md` file for details.
