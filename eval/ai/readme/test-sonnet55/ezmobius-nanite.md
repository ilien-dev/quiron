# nanite

**A self-assembling fabric of Ruby daemons.**

Nanite turns a handful of small Ruby processes into a cooperative mesh. You start
daemons on any machines you like, and they find each other, agree on who does
what, and rebuild the mesh when members come and go. There is no central
coordinator to deploy, no service registry to babysit, and no cluster manifest to
keep in sync.

```
   ┌────────┐      ┌────────┐      ┌────────┐
   │ nanite │◄────►│ nanite │◄────►│ nanite │
   │ (web)  │      │(worker)│      │(worker)│
   └───┬────┘      └───┬────┘      └────────┘
       │               │
       └───────┬───────┘
            ┌──▼─────┐
            │ nanite │
            │(sched) │
            └────────┘
```

## Why nanite?

Most job and service frameworks assume infrastructure: a broker, a database, a
leader election service. Nanite assumes only Ruby and a network. Each daemon is
small, does one kind of work, and carries enough knowledge about the rest of the
fabric to stand in for any neighbor that disappears.

Use nanite when you want:

- **Zero-config clustering.** Start a daemon and it joins the fabric.
- **Graceful degradation.** Losing a node reduces capacity, not availability.
- **Small, composable units.** Each daemon is a plain Ruby class with a few hooks.
- **Easy local development.** The whole fabric runs on a laptop in one terminal.

Nanite is probably not the right tool if you need strict exactly-once delivery,
multi-datacenter consensus, or sub-millisecond latency.

## Features

- Peer discovery over multicast, DNS, or a static seed list
- Gossip-based membership with failure detection
- Role negotiation: daemons advertise capabilities and claim work they can do
- Automatic rebalancing when nodes join, leave, or fail
- Pluggable transports (TCP by default, Unix sockets for local fabrics)
- Structured logging and a built-in status endpoint
- No required external services

## Requirements

- Ruby 3.2 or newer
- Linux, macOS, or Windows (Windows uses TCP transport only)

## Installation

Add nanite to your Gemfile:

```ruby
gem "nanite"
```

Then install:

```sh
bundle install
```

Or install it directly:

```sh
gem install nanite
```

## Quick start

Define a daemon. A daemon declares what it can do and how it handles work:

```ruby
# daemons/resizer.rb
class Resizer < Nanite::Daemon
  capability :image_resize
  replicas   min: 2, max: 8

  def handle(job)
    image = Vips::Image.new_from_file(job.payload[:path])
    image.resize(job.payload[:scale]).write_to_file(job.payload[:out])
    job.complete(out: job.payload[:out])
  end
end
```

Start it:

```sh
nanite up daemons/resizer.rb
```

On another terminal or another machine, start a second one. No address required:

```sh
nanite up daemons/resizer.rb
```

The two daemons discover each other and form a fabric. Check on it:

```sh
nanite status
```

```
FABRIC  4f2a91  (2 nodes, healthy)
NODE      ROLE          LOAD   UPTIME
a1c3      image_resize  0.12   00:04:11
b7e0      image_resize  0.08   00:00:37
```

Submit work from anywhere that can reach the fabric:

```ruby
require "nanite"

fabric = Nanite.connect
result = fabric.call(:image_resize, path: "in.png", scale: 0.5, out: "out.png")
puts result[:out]
```

## How it works

### Discovery

When a daemon boots, it looks for peers in this order:

1. Addresses in `seeds` from the configuration
2. DNS SRV records, if `discovery.dns` is set
3. Multicast announcements on the local network

As soon as it reaches one peer, it learns about the rest through gossip. Seeds
are only an introduction. Once a node has joined, losing every seed is harmless.

### Membership and failure detection

Each node periodically exchanges a compact membership digest with a few random
peers. A node that misses several rounds is marked *suspect*, then *down* if no
peer can vouch for it. Suspicion is shared, so one flaky link does not evict a
healthy node.

### Roles and assembly

Every daemon advertises one or more **capabilities**. The fabric tracks how many
healthy replicas of each capability exist and compares that to the `replicas`
range each daemon declares.

If a capability falls below its minimum, a node with spare capacity and the right
code can *adopt* the role. A general-purpose daemon (`Nanite::Daemon` with
`adopts: [...]`) can pick up roles dynamically, which is how the fabric heals
itself. If a capability exceeds its maximum, surplus replicas go idle or release
the role.

### Work routing

Jobs are routed to a replica of the requested capability using least-loaded
selection with a small random jitter to avoid herding. If a replica dies mid-job,
the job is retried on another replica, up to the retry limit. Handlers should be
idempotent. Nanite provides at-least-once delivery.

## Configuration

Nanite reads `nanite.yml` from the working directory, or the path in
`NANITE_CONFIG`. Every key is optional.

```yaml
fabric: production          # nodes only join fabrics with the same name
bind: 0.0.0.0:7400
seeds:
  - 10.0.0.5:7400
  - 10.0.0.6:7400

discovery:
  multicast: true
  dns: _nanite._tcp.example.internal

gossip:
  interval: 1s
  fanout: 3
  suspect_after: 5s

jobs:
  retries: 3
  timeout: 30s

auth:
  shared_secret_env: NANITE_SECRET

log:
  level: info
  format: json
```

Environment variables override file values using the pattern
`NANITE_GOSSIP_INTERVAL=2s`.

## Command line

| Command | Purpose |
| --- | --- |
| `nanite up FILE...` | Start a daemon from one or more files |
| `nanite status` | Show fabric membership and load |
| `nanite drain NODE` | Stop accepting work on a node and hand off its roles |
| `nanite call CAP JSON` | Submit a job from the shell |
| `nanite console` | Open an IRB session connected to the fabric |

Run `nanite help COMMAND` for flags.

## Security

Fabrics are open by default so that local development is painless. **Do not run
an open fabric on an untrusted network.** In production:

- Set `auth.shared_secret_env` so nodes authenticate each other with HMAC-signed
  messages
- Enable `transport.tls` to encrypt traffic between nodes
- Bind to a private interface rather than `0.0.0.0`
- Use a distinct `fabric` name per environment

Handlers execute arbitrary Ruby you wrote. Nanite does not sandbox them, and
nodes that adopt roles load code from their own filesystem, never from the
network.

## Testing your daemons

Nanite ships a test harness that runs an in-process fabric with a virtual clock:

```ruby
require "nanite/testing"

RSpec.describe Resizer do
  it "survives losing a replica" do
    fabric = Nanite::Testing.fabric(Resizer => 3)
    fabric.kill(fabric.nodes.first)
    fabric.advance(10)

    expect(fabric.replicas(:image_resize)).to eq(2)
    expect(fabric.call(:image_resize, path: "a.png", scale: 1, out: "b.png")).to be_ok
  end
end
```

## Roadmap

- [ ] Persistent job queues for fabrics that must survive total restarts
- [ ] Weighted capabilities and node labels (zone, GPU, memory)
- [ ] Web dashboard
- [ ] Rolling upgrades with version-aware role handoff

## Contributing

Bug reports and pull requests are welcome.

```sh
git clone https://github.com/your-org/nanite
cd nanite
bundle install
bundle exec rake test
```

Please include a test with any behavior change. For larger changes, open an issue
first so we can talk through the design. Run `bundle exec rubocop` before
submitting.

## License

Released under the MIT License. See `LICENSE` for details.
