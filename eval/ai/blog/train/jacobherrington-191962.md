# Give Your Terminal Super Powers: tmux Cheatsheet!

If you spend much of your day in a terminal, `tmux` can transform the way you work. It lets you create persistent terminal sessions, split your screen into panes, organize tasks into windows, and reconnect after losing an SSH connection.

Think of `tmux` as a window manager for your terminal—with super powers.

This cheatsheet covers the commands you need to become productive quickly.

## The tmux Mental Model

tmux organizes terminals into three layers:

- **Session:** A persistent workspace containing one or more windows.
- **Window:** Similar to a browser tab.
- **Pane:** A section created by splitting a window.

A session might represent one project. Inside it, you could have separate windows for your editor, server, tests, and logs. Each window can then be divided into panes.

Most tmux shortcuts begin with a **prefix key**. The default prefix is:

```text
Ctrl-b
```

For example, to create a new window, press `Ctrl-b`, release both keys, and then press `c`.

Throughout this article, `Prefix` means `Ctrl-b`.

## Starting and Managing Sessions

Start tmux:

```bash
tmux
```

Create a named session:

```bash
tmux new -s myproject
```

Named sessions are much easier to find later.

Detach from the current session without stopping it:

```text
Prefix d
```

List running sessions:

```bash
tmux ls
```

Attach to the most recent session:

```bash
tmux attach
```

Attach to a named session:

```bash
tmux attach -t myproject
```

Rename the current session:

```text
Prefix $
```

Kill a session from outside tmux:

```bash
tmux kill-session -t myproject
```

Kill every tmux session:

```bash
tmux kill-server
```

Be careful with that last command—it closes everything managed by tmux.

## Working with Windows

Windows are ideal for separating major activities. You might keep your editor in one window, tests in another, and application logs in a third.

Create a window:

```text
Prefix c
```

Rename the current window:

```text
Prefix ,
```

Move to the next or previous window:

```text
Prefix n
Prefix p
```

Jump directly to a numbered window:

```text
Prefix 0
Prefix 1
Prefix 2
```

Display an interactive window list:

```text
Prefix w
```

Return to the previously active window:

```text
Prefix l
```

Close the current window:

```text
Prefix &
```

You can also close a window by exiting every shell running inside it:

```bash
exit
```

## Splitting Windows into Panes

Panes let you view multiple terminals simultaneously. This is especially useful when running a development server while editing code or watching logs.

Split the current pane vertically:

```text
Prefix %
```

Split it horizontally:

```text
Prefix "
```

Move between panes with the arrow keys:

```text
Prefix ←
Prefix →
Prefix ↑
Prefix ↓
```

Cycle through panes:

```text
Prefix o
```

Show pane numbers:

```text
Prefix q
```

After the numbers appear, press one to jump directly to that pane.

Close the active pane:

```text
Prefix x
```

Temporarily expand the active pane to fill the window:

```text
Prefix z
```

Press the same shortcut again to restore the layout. Zooming is extremely useful when a command produces dense output.

Rotate panes:

```text
Prefix Ctrl-o
```

Cycle through built-in layouts:

```text
Prefix Space
```

## Resizing Panes

The default resizing shortcuts require holding the prefix while pressing an arrow key:

```text
Prefix Ctrl-←
Prefix Ctrl-→
Prefix Ctrl-↑
Prefix Ctrl-↓
```

Depending on your terminal, these combinations may not work reliably. Command mode provides an alternative:

```text
Prefix :
```

Then enter:

```text
resize-pane -L 5
resize-pane -R 5
resize-pane -U 3
resize-pane -D 3
```

The final number specifies how many cells to resize.

## Copy Mode and Scrollback

Normal terminal scrolling can feel confusing inside tmux because tmux manages its own history.

Enter copy mode:

```text
Prefix [
```

Use arrow keys or Page Up and Page Down to navigate. Press `q` to leave copy mode.

Search backward:

```text
Ctrl-r
```

Search forward:

```text
Ctrl-s
```

These search shortcuts depend on the configured copy-mode key table.

To use Vim-style navigation, add this to `~/.tmux.conf`:

```tmux
setw -g mode-keys vi
```

Then copy text with:

1. `Prefix [` to enter copy mode.
2. Move to the beginning of the text.
3. Press `Space` to begin selecting.
4. Move to the end.
5. Press `Enter` to copy.

Paste the tmux buffer with:

```text
Prefix ]
```

## Command Mode

Command mode exposes features that do not have convenient shortcuts.

Open it with:

```text
Prefix :
```

Useful commands include:

```tmux
new-window
split-window
rename-session new-name
rename-window new-name
list-keys
source-file ~/.tmux.conf
```

You can also press:

```text
Prefix ?
```

to browse every available key binding.

## A Practical Configuration

tmux reads configuration from `~/.tmux.conf`. Here is a small starting point:

```tmux
# Start window and pane numbering at 1
set -g base-index 1
setw -g pane-base-index 1

# Automatically fix numbering after closing a window
set -g renumber-windows on

# Increase scrollback history
set -g history-limit 50000

# Enable mouse support
set -g mouse on

# Use Vim-style keys in copy mode
setw -g mode-keys vi

# Reload configuration
bind r source-file ~/.tmux.conf \; display-message "Config reloaded"
```

Reload it without restarting tmux:

```text
Prefix r
```

Mouse support lets you select panes, resize them, change windows, and scroll through history. It is convenient, although learning the keyboard shortcuts remains worthwhile.

## A Simple Development Workflow

Create a project session:

```bash
tmux new -s api
```

Use the first window for your editor:

```bash
nvim .
```

Create another window for the development server:

```text
Prefix c
```

```bash
npm run dev
```

Rename it:

```text
Prefix ,
```

Create a third window for tests, then split it to monitor logs:

```text
Prefix c
Prefix %
```

Detach when you are finished:

```text
Prefix d
```

Later, restore the complete workspace:

```bash
tmux attach -t api
```

Your programs, pane layout, terminal history, and long-running processes will still be there.

## Essential Shortcuts at a Glance

| Action | Shortcut |
|---|---|
| Detach session | `Prefix d` |
| Create window | `Prefix c` |
| Next window | `Prefix n` |
| Previous window | `Prefix p` |
| Rename window | `Prefix ,` |
| Vertical split | `Prefix %` |
| Horizontal split | `Prefix "` |
| Change pane | `Prefix Arrow` |
| Close pane | `Prefix x` |
| Zoom pane | `Prefix z` |
| Enter copy mode | `Prefix [` |
| Paste buffer | `Prefix ]` |
| Open command mode | `Prefix :` |
| Show shortcuts | `Prefix ?` |

## Final Thoughts

tmux may feel awkward for the first few days because every action begins with a prefix. That small learning curve pays off quickly.

Start with four skills: create a named session, detach and reattach, create windows, and split panes. Once those become muscle memory, add copy mode, custom key bindings, and a personal configuration.

Your terminal will stop being a collection of disposable tabs and become a persistent, organized development workspace.