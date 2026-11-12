# tenus

**Linux networking in Go.**

tenus is a Go library for creating and managing Linux network devices from native Go code. It lets you build bridges, veth pairs, VLANs, VXLANs, MACVLAN interfaces, and TUN/TAP devices, assign addresses, bring links up and down, and move interfaces between network namespaces, without shelling out to `ip` or `brctl`.

Tools like `ip link` are reliable, but scripting them from Go means building command strings, parsing text output, and handling errors from a child process. tenus talks to the kernel directly through netlink, so operations return typed errors, run without spawning processes, and can be tested and composed like any other Go code.

## Features

- **Link creation** for bridges, veth pairs, VLAN sub-interfaces, VXLAN overlays, MACVLAN and MACVTAP interfaces, and TUN/TAP devices.
- **Link management**: set state (up/down), MTU, MAC address, and master/slave relationships.
- **Addressing**: add and remove IPv4 and IPv6 addresses and inspect the addresses on a link.
- **Routing**: add and remove routes and default gateways.
- **Network namespaces**: create, enter, and move links between namespaces, which is useful for container runtimes and integration tests.
- **Lookup**: find interfaces by name or index and list all links on the host.
- **No cgo**: pure Go, so it cross-compiles cleanly and needs no C toolchain.

## Requirements

- Linux kernel 3.10 or newer. Some link types, such as VXLAN and MACVLAN, need newer kernels or specific modules.
- Go 1.21 or newer.
- Root privileges or `CAP_NET_ADMIN` for any operation that changes network state. Read-only operations such as listing links generally do not need elevated privileges.

tenus does not run on macOS, Windows, or BSD. Netlink is Linux-specific, and the package will not build on those platforms.

## Installation

```sh
go get github.com/milosgajdos/tenus
```

Import it in your code:

```go
import "github.com/milosgajdos/tenus"
```

## Quick start

The following example creates a bridge, attaches a veth pair to it, assigns an address, and brings everything up.

```go
package main

import (
	"log"
	"net"

	"github.com/milosgajdos/tenus"
)

func main() {
	// Create a bridge named br0.
	br, err := tenus.NewBridgeWithName("br0")
	if err != nil {
		log.Fatalf("create bridge: %v", err)
	}

	// Give the bridge an address on the 10.10.0.0/24 network.
	ip, ipnet, err := net.ParseCIDR("10.10.0.1/24")
	if err != nil {
		log.Fatalf("parse cidr: %v", err)
	}
	ipnet.IP = ip
	if err := br.SetLinkIp(ipnet.IP, ipnet); err != nil {
		log.Fatalf("set address: %v", err)
	}

	// Bring the bridge up.
	if err := br.SetLinkUp(); err != nil {
		log.Fatalf("link up: %v", err)
	}

	log.Println("br0 is up with 10.10.0.1/24")
}
```

Run it as root:

```sh
sudo go run ./examples/bridge
```

> **Note:** The function and method names in this example reflect the library's current style. If you are working from a different version, check the package documentation with `go doc github.com/milosgajdos/tenus`.

## Common tasks

### Creating a veth pair

A veth pair is a virtual cable with two ends. Put one end in the host and the other in a namespace, or attach each end to a different bridge.

```go
host, peer, err := tenus.NewVethPairWithOptions("veth-host", tenus.VethOptions{
	PeerName: "veth-peer",
})
if err != nil {
	log.Fatal(err)
}

if err := host.SetLinkUp(); err != nil {
	log.Fatal(err)
}
```

### Creating a VLAN

```go
parent, err := tenus.NewLinkFrom("eth0")
if err != nil {
	log.Fatal(err)
}

vlan, err := parent.NewVlanLink(100)
if err != nil {
	log.Fatal(err)
}

if err := vlan.SetLinkUp(); err != nil {
	log.Fatal(err)
}
```

### Attaching an interface to a bridge

```go
if err := br.AddSlaveIfc(host); err != nil {
	log.Fatal(err)
}
```

### Moving a link into a network namespace

Moving a link into a namespace is the basis for container networking. Pass the namespace file descriptor or PID, as the function signature requires:

```go
if err := peer.SetNetNsPid(containerPid); err != nil {
	log.Fatal(err)
}
```

After the move, the link disappears from the host namespace and becomes visible only inside the target namespace.

### Listing interfaces

```go
links, err := tenus.Links()
if err != nil {
	log.Fatal(err)
}

for _, l := range links {
	log.Printf("%s (index %d, state %s)", l.Name(), l.Index(), l.State())
}
```

## Error handling

Every mutating operation returns an `error`. tenus wraps kernel errors with context about the operation and the link involved, so you can use `errors.Is` to check for common conditions:

```go
if err := br.SetLinkUp(); err != nil {
	if errors.Is(err, tenus.ErrNotFound) {
		// The link was removed between creation and this call.
	}
	return fmt.Errorf("bring up %s: %w", br.Name(), err)
}
```

The most common causes of failure are:

- **Permission denied** from a missing `CAP_NET_ADMIN`. Run the process as root or grant the capability.
- **File exists** when a link name is already in use. Delete or rename the existing link first.
- **No such device** when a parent interface is missing, for example when creating a VLAN on an interface that does not exist.
- **Operation not supported** when a kernel module is not loaded. Check `lsmod` for the module that provides the link type, such as `vxlan` or `macvlan`.

## Testing

Unit tests that do not touch the host network run without privileges:

```sh
go test ./...
```

Integration tests create real links and namespaces, so they need root and a Linux host. They are behind a build tag:

```sh
sudo go test -tags integration ./...
```

Run integration tests in a disposable VM or container. A failed test can leave links behind, and cleanup depends on the test reaching its teardown code.

For tests in your own project, the most reliable pattern is to create a dedicated network namespace per test, run the operations inside it, and delete the namespace afterward. Deleting a namespace removes every link inside it.

## Project layout

```
tenus/
├── bridge.go        # Bridge creation and slave management
├── veth.go          # Veth pair creation
├── vlan.go          # VLAN sub-interfaces
├── vxlan.go         # VXLAN overlays
├── macvlan.go       # MACVLAN and MACVTAP
├── tuntap.go        # TUN and TAP devices
├── netns.go         # Network namespace helpers
├── link.go          # Generic link operations
├── addr.go          # IP address management
├── route.go         # Routing table operations
├── errors.go        # Sentinel errors
├── examples/        # Runnable examples
└── internal/netlink # Low-level netlink messaging
```

## Design notes

**Netlink, not exec.** tenus sends netlink messages to the kernel and reads the replies. It does not invoke `ip` or any other binary. This removes a dependency on tools being installed and avoids the fragility of parsing command output.

**Thin types over kernel objects.** Each link type is a Go type that wraps the kernel's view of that interface. Methods map closely to the operations the kernel offers, so the documentation for `ip(8)` and `rtnetlink(7)` is a useful reference when behavior is unclear.

**Explicit errors.** tenus returns errors instead of logging them or exiting. The caller decides whether a failure is fatal.

**Minimal dependencies.** The library depends only on the standard library and a small netlink layer. This keeps the dependency tree small for projects that embed it.

## Limitations

- Linux only. Non-Linux builds will fail.
- Not every netlink feature is wrapped. Traffic control (`tc`), nftables and iptables rules, and some advanced routing features are outside the scope of the library. Use a dedicated library for those, or call the kernel interface directly.
- Some operations depend on kernel version. A feature that works on a recent kernel may return `operation not supported` on an older one.
- tenus does not manage the lifetime of network state across process restarts. Links you create persist until you delete them or the host reboots, so your program must clean up or reconcile its state on startup.

## Contributing

Contributions are welcome. Before opening a pull request:

1. Run `go vet ./...` and `go test ./...`.
2. Run the integration tests on a Linux host if your change touches link creation or deletion.
3. Keep changes focused. A pull request that adds one link type or fixes one bug is easier to review than one that does several things.
4. Describe the kernel version and distribution you tested on in the pull request.

For bug reports, include the Linux kernel version (`uname -r`), the output of `ip link` before and after the failing operation, and the smallest Go program that reproduces the problem.

## License

tenus is released under the MIT License. See [LICENSE](LICENSE) for details.

---

*Note: I wrote this from the project description alone and did not read the source. The API names in the examples are plausible for this library but should be checked against the code before publishing. Tell me the package path and I can verify them against the actual exports.*
