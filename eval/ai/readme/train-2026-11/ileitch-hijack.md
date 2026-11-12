# hijack

**Provides an irb session to a running ruby process.**

Hijack lets you attach an interactive Ruby console to a process that is already running, without restarting it and without having planned for it in advance. You can inspect live objects, check the state of caches and connection pools, call methods, and diagnose problems that only show up in production after hours or days of uptime.

If you have ever wished you could "just open irb inside" a misbehaving daemon, worker, or web server, hijack is for you.

---

## Why hijack?

Many bugs are hard to reproduce locally. A memory leak appears only after a week of traffic. A background worker stalls on one specific job. A cache holds stale data that nobody can explain. Restarting the process destroys the evidence, and adding logging means redeploying and waiting for the problem to come back.

Hijack takes a different approach. It connects to the target process as it is right now and gives you a familiar irb prompt running *inside* that process. Everything you type is evaluated in the target's object space, so you see the real state rather than a reconstruction of it.

## Features

- **Attach to any running Ruby process** by PID, with no changes to the target's code.
- **Full irb experience**, including history and tab completion where your environment supports them.
- **Evaluate code in the remote process.** Objects, constants, globals and loaded libraries are all available.
- **Output forwarding.** Anything the target writes to `$stdout` or `$stderr` while you are connected can be mirrored to your terminal.
- **Clean detach.** Exiting the session leaves the target running as it was.

## Requirements

- A Unix-like operating system (Linux or macOS)
- Ruby, matching the version used by the target process
- `gdb`, used to inject the bootstrap code into the target
- Permission to trace the target process (the same user, or root)

On Linux systems with Yama ptrace restrictions enabled, you may need to adjust `/proc/sys/kernel/yama/ptrace_scope` or run hijack with elevated privileges.

## Installation

Install the gem:

```sh
gem install hijack
```

Or add it to your Gemfile:

```ruby
gem 'hijack'
```

Then run `bundle install`.

## Usage

Find the PID of the process you want to inspect:

```sh
ps aux | grep ruby
```

Then attach to it:

```sh
hijack 12345
```

After a moment you will see a prompt. You are now evaluating code inside process 12345:

```
=> Hijacking...
=> Mirroring: stdout, stderr
=> Connected
>> Process.pid
=> 12345
>> ObjectSpace.each_object(Class).count
=> 4821
>> MyApp::Cache.size
=> 10293
```

To leave the session, type `exit` or press `Ctrl-D`. The target process continues running.

### Common options

```
hijack [options] PID

    -g, --gdb-path PATH     Path to the gdb binary
    -m, --mirror STREAMS    Streams to mirror (stdout, stderr, or none)
    -d, --debug             Print debugging information while attaching
    -h, --help              Show help
```

## How it works

Hijack works in a few stages:

1. **Injection.** Hijack uses `gdb` to briefly pause the target and make it evaluate a small piece of Ruby code. That code starts a DRb (Distributed Ruby) server inside the target, listening on a local socket.
2. **Resume.** The target is resumed immediately. The DRb server runs in its own thread, so the application keeps doing its normal work.
3. **Connection.** Hijack starts a local irb session whose evaluation context is proxied over DRb. Each line you enter is sent to the target, evaluated there, and the result is returned to your terminal.
4. **Teardown.** When you exit, the DRb server is shut down and the target is left as it was before you connected.

The pause in step 1 is normally very short, but it is a real pause. Keep that in mind on latency-sensitive systems.

## Safety and caveats

Hijack gives you the full power of Ruby inside a live process. That is the point, and it is also the risk.

- **You can change state.** Reassigning a constant, clearing a cache or calling a destructive method affects the real process immediately. Be deliberate.
- **Long-running expressions block.** Code you evaluate runs inside the target. An expensive loop or a blocking call can stall other threads, especially under the GVL.
- **Return values are serialized.** Results travel back over DRb. Very large objects, or objects that cannot be marshalled, may be slow to display or returned as references.
- **Use in production with care.** Hijack is excellent for diagnosis, but treat a hijack session like an SSH session on a production box: limit who can use it and know what you are running.
- **Version mismatch.** Using a different Ruby version from the target can cause confusing failures during injection or serialization.

## Troubleshooting

**"Could not attach to process"**
Check that you own the process or are running as root, and that ptrace is allowed on your system.

**The session hangs on "Hijacking..."**
The target may be blocked in a system call or holding the GVL in a C extension. Try again with `--debug` to see where injection stops.

**gdb not found**
Install gdb with your package manager, or pass its location with `--gdb-path`.

## Contributing

Bug reports and pull requests are welcome. Please include your Ruby version, operating system, and gdb version when reporting problems, along with the output of `hijack --debug` if relevant.

1. Fork the repository
2. Create a feature branch
3. Add tests for your change
4. Open a pull request

## License

Hijack is released under the MIT License. See `LICENSE` for details.
