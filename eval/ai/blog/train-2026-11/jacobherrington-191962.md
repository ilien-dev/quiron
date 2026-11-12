# Give Your Terminal Super Powers: tmux Cheatsheet!

You have a development server running, logs streaming, and another terminal open for Git. Then your SSH connection drops, taking your carefully arranged workspace with it.

Sound familiar?

Meet **tmux**, a terminal multiplexer that lets you organize multiple shells inside one terminal and reconnect to sessions you left running. Once a few shortcuts become muscle memory, juggling terminal windows starts feeling surprisingly unnecessary.

This cheatsheet covers the commands you’ll actually use, plus a small configuration and a practical workflow to get you started.

First, one detail: shortcuts below assume tmux’s default key bindings. If you’re using someone else’s configuration, some keys may behave differently.

## Start with three building blocks

Before memorizing shortcuts, understand how tmux organizes your workspace:

- **Session:** A collection of terminal work, usually belonging to one project.
- **Window:** A workspace inside a session, similar to a browser tab.
- **Pane:** A visible terminal region within a window.

For example, your `shop` session might contain an `editor` window and a `server` window. The server window could have two panes: one running your application and another showing logs.

These concepts, along with detaching and reconnecting, are explained in the [official tmux getting started guide](https://github.com/tmux/tmux/wiki/Getting-Started).

## Install tmux

Use your operating system’s package manager.

```bash
# macOS with Homebrew
brew install tmux

# Ubuntu / Debian
sudo apt update
sudo apt install tmux

# Fedora
sudo dnf install tmux
```

On Windows, you can install tmux inside a Linux distribution running through WSL.

Check that it’s available:

```bash
tmux -V
```

Then create your first named session:

```bash
tmux new -s playground
```

You’ll land in a shell with a status bar along the bottom. That shell is now running inside tmux.

## Learn the prefix

Most tmux shortcuts begin with **Ctrl + b**, called the prefix.

When this article says `Prefix → c`, press **Ctrl + b**, release both keys, then press **c**.

You don’t hold all three keys together.

Try `Prefix → ?` to open the built-in shortcut reference. Press `q` to leave the help view.

That shortcut is particularly useful when you remember that an action exists but forget which key triggers it.

## Sessions: leave and come back

Sessions make it easy to keep different projects organized.

Run these commands from your shell:

```bash
# Create a named session
tmux new -s myapp

# List existing sessions
tmux ls

# Reconnect to a specific session
tmux attach -t myapp

# Attach if it exists; otherwise create it
tmux new -A -s myapp
```

Inside tmux, use:

| Shortcut | Action |
| --- | --- |
| `Prefix → d` | Detach from the session |
| `Prefix → s` | Open the session picker |
| `Prefix → $` | Rename the current session |

Detaching leaves your programs running. You can reconnect later and continue working.

For remote work, start tmux **on the remote machine after connecting over SSH**. A local tmux session cannot preserve a remote process simply by keeping your local SSH client open.

## Windows: give each task a home

Windows help you separate activities without leaving your session.

| Shortcut | Action |
| --- | --- |
| `Prefix → c` | Create a window |
| `Prefix → ,` | Rename the current window |
| `Prefix → n` | Go to the next window |
| `Prefix → p` | Go to the previous window |
| `Prefix → 0` … `9` | Select a window by number |
| `Prefix → w` | Browse windows |
| `Prefix → &` | Kill the current window, after confirmation |

Try names like `editor`, `server`, and `git`. Descriptive names make the status bar easier to scan than several windows all displaying your shell’s name.

## Panes: see things together

Panes are useful when two tasks benefit from being visible simultaneously.

| Shortcut | Action |
| --- | --- |
| `Prefix → %` | Split into left and right panes |
| `Prefix → "` | Split into top and bottom panes |
| `Prefix → Arrow key` | Move to another pane |
| `Prefix → o` | Cycle through panes |
| `Prefix → z` | Toggle zoom for the active pane |
| `Prefix → Space` | Cycle through layouts |
| `Prefix → x` | Kill the active pane, after confirmation |

Zoom is especially handy for reading a long error message. Press the same shortcut again to restore the surrounding panes.

For precise resizing, open the command prompt with `Prefix → :` and enter:

```text
resize-pane -R 10
```

This expands the active pane to the right where the layout permits. Use `-L`, `-U`, or `-D` for other directions.

## Scroll through previous output

When you need to inspect output that has already disappeared above the screen, enter copy mode:

```text
Prefix → [
```

Use the arrow keys or Page Up to navigate. Press `q` to return to normal terminal input.

Copy mode also supports selecting and copying text, but those bindings depend on whether tmux uses Emacs or vi mode. Check `man tmux` for your configuration.

## Add a little comfort

Put these settings in `~/.tmux.conf`:

```tmux
# Allow mouse interaction
set -g mouse on

# Keep more scrollback
set -g history-limit 50000
```

Reload the file from a shell inside tmux:

```bash
tmux source-file ~/.tmux.conf
```

Mouse support makes pane selection and resizing approachable while you learn the keyboard shortcuts.

## Try a five-minute workflow

Create a session called `demo`. Rename its first window `server`, then start your development server.

Split the window and run your log command beside it. Create another window called `git` for commits and repository checks.

Now detach, list your sessions, and reconnect.

That exercise teaches the core loop: organize your tools, leave them running, and return when you need them.

Start with five shortcuts: create a window, split a pane, switch panes, zoom, and detach. Add the rest as your workflow demands them.

Which tmux shortcut would earn a permanent place in your daily routine?
