# RobotS

**Actor system for Rust.**

RobotS lets you build concurrent, fault-tolerant programs out of small, isolated units of state and behavior called actors. Actors never share memory. They communicate by sending messages, process one message at a time, and are organized into supervision trees that decide what happens when something goes wrong.

[![crates.io](https://img.shields.io/crates/v/robots.svg)](https://crates.io/crates/robots)
[![docs.rs](https://docs.rs/robots/badge.svg)](https://docs.rs/robots)
[![license](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue.svg)](#license)

---

## Why actors?

Shared-memory concurrency is hard to reason about even with Rust's guarantees. Locks pile up, channels get tangled, and error handling gets scattered across threads. The actor model offers a simpler mental picture:

- Each actor owns its state. Nobody else can touch it.
- The only way to interact with an actor is to send it a message.
- An actor handles one message at a time, so you never need a lock inside it.
- Failures are contained. A crashing actor is handled by its parent, not by whoever happened to be calling it.

Rust's ownership model fits this well: messages are moved between actors, and the type system checks what can cross the boundary.

## Features

- **Typed actors and messages.** Each actor declares the message types it accepts, and the compiler rejects anything else.
- **Lightweight actors.** Spawn thousands of actors cheaply. They are scheduled onto a small pool of worker threads rather than getting an OS thread each.
- **Supervision trees.** Parents supervise children and choose to resume, restart, stop, or escalate on failure.
- **Fire-and-forget and request/response.** Use `tell` for one-way messages and `ask` for a future that resolves with a reply.
- **Bounded and unbounded mailboxes.** Pick a backpressure strategy per actor.
- **Timers and scheduling.** Send a message after a delay or on a fixed interval.
- **Lifecycle hooks.** Run code on start, stop, and restart.
- **Graceful shutdown.** Stop a subtree and wait for children to finish draining their mailboxes.
- **Test utilities.** Deterministic helpers for testing actors without sleeping.

## Installation

Add RobotS to your `Cargo.toml`:

```toml
[dependencies]
robots = "0.1"
```

RobotS requires a recent stable Rust toolchain. See `rust-version` in `Cargo.toml` for the minimum supported version.

## Quick start

A small actor that counts things:

```rust
use robots::{Actor, ActorSystem, Context, Handler, Message, Props};

// 1. Define the messages.
struct Increment(u64);
struct Get;

impl Message for Increment { type Reply = (); }
impl Message for Get       { type Reply = u64; }

// 2. Define the actor and its state.
#[derive(Default)]
struct Counter {
    total: u64,
}

impl Actor for Counter {}

// 3. Implement a handler for each message type.
impl Handler<Increment> for Counter {
    fn handle(&mut self, msg: Increment, _ctx: &mut Context<Self>) {
        self.total += msg.0;
    }
}

impl Handler<Get> for Counter {
    fn handle(&mut self, _msg: Get, _ctx: &mut Context<Self>) -> u64 {
        self.total
    }
}

#[robots::main]
async fn main() {
    // 4. Create a system and spawn an actor.
    let system = ActorSystem::new("demo");
    let counter = system.spawn(Props::new(Counter::default));

    // 5. Send messages.
    counter.tell(Increment(2));
    counter.tell(Increment(3));

    let total = counter.ask(Get).await.unwrap();
    assert_eq!(total, 5);

    system.shutdown().await;
}
```

Run it with:

```sh
cargo run --example counter
```

## Core concepts

### Actors

An actor is a struct that implements `Actor`. Its fields are its private state. It reacts to messages through one or more `Handler<M>` implementations. Because the runtime calls handlers one at a time, handlers take `&mut self` and need no synchronization.

### Messages

A message is any `Send + 'static` type that implements `Message`. The associated `Reply` type says what, if anything, the sender gets back. Keep messages small and owned. Prefer enums when an actor accepts several related commands.

### Actor references

Spawning returns an `ActorRef<A>`, a cheap, cloneable handle. It is the only way to reach an actor from outside. References stay valid after the actor stops. Sending to a stopped actor returns an error, or routes to dead letters if configured.

### The actor system

`ActorSystem` owns the scheduler, the root of the supervision tree, and the dead-letter queue. Most programs create exactly one.

### Context

Each handler receives a `Context`, which lets the actor spawn children, get a reference to itself, schedule messages, watch other actors, or stop itself.

## Supervision

When a handler panics or returns an error, the failure goes to the actor's parent. The parent's supervision strategy decides what to do:

| Directive  | Effect                                                       |
|------------|--------------------------------------------------------------|
| `Resume`   | Keep the actor and its state, and continue with the next message. |
| `Restart`  | Discard the actor's state, build a fresh instance, and continue.  |
| `Stop`     | Terminate the actor permanently.                             |
| `Escalate` | Pass the failure up to the parent's own supervisor.          |

```rust
use robots::{Directive, Supervisor};
use std::time::Duration;

let props = Props::new(Worker::default).with_supervisor(
    Supervisor::one_for_one()
        .max_restarts(5, Duration::from_secs(60))
        .on_failure(|err| match err {
            Failure::Transient(_) => Directive::Restart,
            Failure::Fatal(_)     => Directive::Escalate,
        }),
);
```

A restart limit prevents a persistently failing actor from looping forever. When the limit is exceeded, the actor is stopped and the failure escalates.

## Request and response

`tell` returns immediately. `ask` returns a future that resolves when the actor replies:

```rust
let reply = tokio::time::timeout(
    Duration::from_secs(1),
    counter.ask(Get),
).await??;
```

Always put a timeout on `ask`. If the target is stuck or has stopped, you want the caller to find out rather than wait forever.

## Mailboxes and backpressure

By default each actor has an unbounded mailbox. For actors that could be overwhelmed, choose a bounded one:

```rust
let props = Props::new(Worker::default)
    .with_mailbox(Mailbox::bounded(1024).overflow(Overflow::DropOldest));
```

Available overflow strategies are `Block`, `DropNewest`, `DropOldest`, and `Fail`.

## Timers

```rust
// Once, after a delay
ctx.schedule_once(Duration::from_secs(5), Tick);

// Repeatedly
let handle = ctx.schedule_interval(Duration::from_millis(250), Tick);
handle.cancel();
```

Timers are cancelled automatically when the owning actor stops.

## Lifecycle hooks

```rust
impl Actor for Worker {
    fn started(&mut self, ctx: &mut Context<Self>)  { /* open connections */ }
    fn stopped(&mut self, ctx: &mut Context<Self>)  { /* release resources */ }
    fn restarting(&mut self, err: &Failure)         { /* log, clean up */ }
}
```

## Testing

The `robots::testkit` module provides a probe actor and a manual clock:

```rust
use robots::testkit::{TestSystem, Probe};

#[test]
fn counter_accumulates() {
    let sys = TestSystem::new();
    let counter = sys.spawn(Props::new(Counter::default));

    counter.tell(Increment(4));
    sys.run_until_idle();

    assert_eq!(sys.block_on(counter.ask(Get)).unwrap(), 4);
}
```

`run_until_idle` processes every queued message before returning, so tests are deterministic. The manual clock lets you advance timers without real waiting.

## Design notes

- **Scheduling.** Actors run on a work-stealing thread pool. A handler runs to completion before another message is delivered to that actor. Long blocking work belongs in a dedicated blocking task, not in a handler.
- **Ordering.** Messages from one sender to one receiver arrive in the order sent. There is no ordering guarantee across different senders.
- **Delivery.** Delivery within a process is at-most-once and reliable unless a bounded mailbox drops messages. RobotS does not hide failure modes. If you need stronger guarantees, build them with acknowledgements and retries.
- **Panics.** A panic inside a handler is caught at the actor boundary and treated as a failure. It never unwinds into other actors.

## Roadmap

- [ ] Remote actors over a pluggable transport
- [ ] Persistent actors with event sourcing
- [ ] Routers (round-robin, consistent-hash, broadcast)
- [ ] Built-in metrics and tracing integration
- [ ] `no_std` core

## Contributing

Contributions are welcome. To get started:

1. Fork the repository and create a branch.
2. Run `cargo fmt`, `cargo clippy --all-targets`, and `cargo test` before opening a pull request.
3. Add tests for new behavior and update docs and examples where relevant.
4. For large changes, open an issue first so we can agree on the approach.

Please be respectful in all project spaces.

## License

Licensed under either of

- Apache License, Version 2.0
- MIT license

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in RobotS by you shall be dual licensed as above, without any additional terms or conditions.
