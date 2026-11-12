# godebug

> **DEPRECATED.** This project is no longer maintained. Please use [Delve](https://github.com/derekparker/delve) instead.

## Status

godebug is deprecated and receives no further development. There will be no bug fixes, new features, or security updates, and issues and pull requests are no longer reviewed. The repository stays online for historical reference only. Please don't start new work on top of it.

The recommended replacement is **Delve**, a mature debugger for Go with active maintainers, wide editor support, and first-class handling of goroutines.

## Why it was deprecated

godebug was created when debugging options for Go were limited and general-purpose debuggers understood Go programs poorly. Delve now covers that need more completely. Rather than split community effort across two tools, we are pointing everyone to one.

Delve offers:

- Native understanding of goroutines, channels, and the Go runtime
- Debugging of running processes, core files, and test binaries
- Integration with VS Code, GoLand, Vim, Emacs, and other editors through its DAP and JSON-RPC servers
- Active development and a much larger contributor base

## Migrating to Delve

### Install

```
go install github.com/go-delve/delve/cmd/dlv@latest
```

Make sure `$GOPATH/bin` (or `$GOBIN`) is on your `PATH`, then confirm the install with:

```
dlv version
```

### Common workflows

| Task                                | Command                |
| ----------------------------------- | ---------------------- |
| Debug the package in the current dir | `dlv debug`            |
| Debug a package's tests             | `dlv test`             |
| Debug a prebuilt binary             | `dlv exec ./myprog`    |
| Attach to a running process         | `dlv attach <pid>`     |

To pass arguments to your program, put them after `--`:

```
dlv debug -- -flag value
```

### A minimal session

```
$ dlv debug
(dlv) break main.main
(dlv) continue
(dlv) next
(dlv) step
(dlv) print someVar
(dlv) locals
(dlv) args
(dlv) bt
(dlv) goroutines
(dlv) exit
```

Type `help` inside the session for the full command list.

### Notes for former godebug users

If your workflow relied on marking breakpoints inside your source code, you can now set them from the debugger with `break <function>` or `break <file>:<line>`. That keeps your source free of debugging markers and removes the need to rebuild just to move a breakpoint.

If you invoked godebug from scripts or CI, replace those calls with the matching `dlv` subcommand from the table above. For non-interactive use, `dlv` can run headless:

```
dlv debug --headless --listen=:2345 --api-version=2
```

You can then connect from your editor or from another `dlv connect` session.

## If you still depend on this repository

- **Remove it** from your dependencies and build scripts when you can.
- **Fork it** if you need to keep a frozen copy. The license in this repository still applies to your fork.
- **Don't expect fixes.** Compatibility with newer Go releases is not guaranteed and will not be addressed here.

## Support and contributions

This repository does not accept new issues, pull requests, or feature requests. For help with debugging Go programs, use the Delve documentation and issue tracker:

- Repository: https://github.com/derekparker/delve
- Documentation: see the `Documentation` directory in that repository

Thank you to everyone who used, tested, and contributed to godebug. Your feedback helped shape what Go debugging looks like today, and we encourage you to bring the same energy to Delve.

## License

See the `LICENSE` file in this repository. The license is unchanged by the deprecation.
