# huptime

**Utility for zero downtime restarts of unmodified programs.**

Restarting a service should not mean making it unavailable. Whether you are deploying a new build, applying configuration changes, or replacing a process that has been running for weeks, the transition should be routine for operators and invisible to users.

huptime helps keep services available while their underlying programs restart. It is designed for situations where the application itself does not provide a graceful restart mechanism—and where modifying the application to add one would be inconvenient, expensive, or impossible.

The goal is straightforward: replace a running program without creating a gap in service.

## Why huptime?

The simplest restart procedure has an obvious weakness:

1. Stop the running program.
2. Start its replacement.
3. Wait for the replacement to become usable.

Between the first step and the last, the service is unavailable. Even a short interruption can cause failed requests, dropped connections, noisy alerts, or unnecessary retries.

Starting the replacement before stopping the original is a better approach, but it introduces coordination problems. The replacement must acquire the resources it needs, become ready to serve traffic, and take over without conflicting with the existing process. Meanwhile, the original may need time to finish work already in progress.

huptime addresses this transition so that applications do not have to implement the entire restart lifecycle themselves.

It is useful when you want to keep an existing program, preserve its normal execution model, and improve how it behaves during operational changes.

## The basic idea

A zero downtime restart is a coordinated handoff between two generations of a program.

The existing generation continues serving while the replacement starts. Once the replacement is ready, responsibility for new work moves to it. The existing generation can then finish outstanding work and exit.

Conceptually, the lifecycle looks like this:

```text
Existing program:  ───── serving ───── draining ─── exit
Replacement:               start ── ready ───── serving ─────
Service:           ───────────── available ──────────────────
```

The important difference from a conventional restart is the overlap. The original program remains available during the replacement’s startup period.

The details of a successful handoff depend on the program, its resources, and the way clients reach it. Treat startup, readiness, traffic transfer, and shutdown as separate events when planning an integration.

## Unmodified programs

huptime is intended for programs that were not written specifically for it.

You should not need to add a restart endpoint, link an application library, or rewrite business logic merely to coordinate process replacement. Your program should retain its ordinary responsibilities: start, perform its work, and respond to its normal operating environment.

However, an unmodified program still has operational characteristics that matter. Before introducing overlapping generations, understand whether it:

- Requires exclusive ownership of a port, file, or device.
- Performs database migrations during startup.
- Creates scheduled jobs or background workers.
- Stores important state only in memory.
- Handles termination gracefully.
- Can safely run alongside another instance.

These characteristics determine how the program should be deployed and what a safe restart means for that service.

## Getting started

Begin with a disposable environment and a representative workload. A successful demonstration should include real requests during a restart, rather than simply showing that a replacement process starts.

Use this sequence to evaluate an integration:

1. **Run the program normally.** Confirm its command, environment, working directory, permissions, and external dependencies.
2. **Define readiness.** Identify an observable condition that means the program can successfully handle work.
3. **Establish a baseline.** Send continuous traffic and record errors, latency, and connection behavior.
4. **Introduce huptime.** Preserve the application’s normal runtime settings while incorporating it into the restart lifecycle.
5. **Exercise a restart.** Keep traffic running throughout startup, handoff, and shutdown.
6. **Test failure cases.** Try an invalid configuration, a failed startup, and an unusually slow replacement.

Installation commands and invocation syntax depend on the distribution and interface provided by your version of huptime. Check its accompanying usage information before integrating commands into deployment automation.

## Readiness matters

A running process is not necessarily a ready service.

A program may need to load configuration, open connections, warm caches, initialize workers, or fetch remote data before it can serve requests. Transferring traffic too early can produce an outage even when both process generations are alive.

Choose a readiness condition that reflects useful behavior. For an HTTP service, that might be a successful request to an endpoint that checks essential dependencies. For another type of program, it might be a protocol exchange or another externally observable result.

Avoid relying solely on a fixed delay. A delay that works on a developer machine may fail during a slow deployment or under production load.

Readiness checks should also have a deadline. A replacement that never becomes ready should produce a clear failure rather than leaving the restart indefinitely unresolved.

## Connections and in-flight work

Service availability and connection continuity are related, but they are different promises.

A service can remain available for new requests while an existing connection is interrupted. Likewise, a listening endpoint can remain reachable even though requests fail during application initialization.

When evaluating huptime with your program, distinguish among:

- Accepting new connections.
- Completing requests already in progress.
- Preserving persistent client sessions.
- Finishing background work.
- Maintaining application-level state.

Long-lived connections deserve particular attention. WebSockets, streaming responses, subscriptions, and interactive sessions may outlive an ordinary deployment window. Decide whether the old generation should wait for them, close them after a deadline, or rely on clients to reconnect.

Document that policy so operators and application owners share the same expectations.

## Configuration and deployments

Keep the replacement’s runtime configuration explicit and reproducible.

Record the executable version, arguments, environment variables, working directory, and configuration files associated with each deployment. This makes a failed restart easier to diagnose and a previous version easier to restore.

Remember that overlapping processes may observe shared resources at the same time. Replacing a configuration file, changing a database schema, or rotating credentials can affect both generations.

Prefer changes that allow the old and new versions to coexist during the handoff. For database changes, this often means separating compatible schema additions from later cleanup.

Zero downtime process replacement works best as one part of a deployment process that also accounts for compatibility.

## Failure handling

A restart should have a clear success condition and a clear failure condition.

If a replacement cannot start or become ready, preserving the healthy existing generation is generally the desired outcome. Verify the actual behavior of your integration before depending on it.

Useful failure scenarios include:

- The replacement executable is missing.
- Configuration validation fails.
- A required dependency is unavailable.
- Startup exceeds its deadline.
- The replacement exits immediately after becoming ready.
- The existing process does not finish shutting down.

Keep logs from both generations accessible during these tests. Include process identifiers or deployment identifiers where possible so that overlapping output remains understandable.

Also define when an operator should intervene and how to return to a known working version.

## Production considerations

Allow capacity for the overlap between generations. During a restart, memory usage, file descriptors, database connections, and CPU demand may temporarily increase.

Check resource limits under realistic load. A replacement that starts successfully in isolation may fail when the original is still consuming most of the machine’s available resources.

Coordinate huptime with any surrounding service manager, container runtime, or deployment system. Make sure each component has a clear responsibility and that competing restart policies do not create loops.

Monitor client-visible behavior throughout deployment. Request success rates and latency are stronger evidence of availability than process counts alone.

## Scope

huptime focuses on restarting programs without an interruption in service. It does not, by itself, establish high availability across machine failures, protect against incompatible releases, or make application state durable.

Those concerns still require appropriate infrastructure and application design.

The practical standard is simple: validate the complete lifecycle with your program, your workload, and your failure conditions. A restart is successful when users can continue their work while the program underneath them changes.
