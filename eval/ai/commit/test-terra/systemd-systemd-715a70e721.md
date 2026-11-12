firewall-util: add nftables backend

Add an nftables backend to the shared firewall utility so that systemd
can manage the NAT rules needed by its networking features on systems
using nftables.

The existing firewall operations provide a common interface for
masquerading traffic from a source network and forwarding a local port
to a remote address. Implement these operations using nftables tables,
chains, sets and maps, with rules that look up the relevant addresses
and ports. This keeps the firewall-specific details inside the utility
and lets its callers continue to express the networking operation they
need without constructing rules themselves.

Use the netfilter netlink interface to create and update the nftables
objects. Keep systemd's NAT configuration in its own table so that the
objects it manages can be identified separately from rules installed by
an administrator or another service. Source address ranges can be added
to or removed from a set for masquerading; local port forwarding can
use a map to associate a protocol and port with a destination.

Initialize the required table, chains and rules before adding entries.
If the table has been removed, for example by a ruleset flush,
recreate the required objects when a subsequent operation needs them.
Propagate errors from netlink operations to the caller so that a failed
firewall update is visible to the component requesting it.

This provides a path for systemd's networking features to work with
native nftables while retaining the existing firewall utility interface.
