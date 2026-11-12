xen: allow limiting the amount of duplicated pending xenstore watches

Xenstore watches notify a guest when a watched path changes. When the
same path is watched repeatedly, each registration can queue its own
pending event. A misbehaving or malicious peer that keeps re-registering
the same watch can make the pending queue grow without bound and consume
kernel memory.

Add a tunable that caps how many duplicate pending watch events may be
queued for a single watch path. Once the cap is reached, further
duplicates are dropped instead of being appended. Unique events are
unaffected, and the default keeps the previous behaviour for workloads
that never reach the limit.

Exposing the limit as a sysctl lets administrators tune it for their
environment without rebuilding the kernel.
