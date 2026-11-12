Sort out the mess around writable replicas and lookupKeyRead/Write

The key lookup helpers had accumulated overlapping checks for replica
state. Whether a lookup could delete an expired key, update access
statistics, or touch LRU/LFU metadata depended on a mix of conditions
spread across lookupKeyRead, lookupKeyWrite, and their callers. These
conditions did not always agree on how a writable replica should
behave, which made the resulting behavior hard to reason about.

This change gathers the replica-related decisions in one place so that
lookups follow the same rules everywhere. Writes issued to a writable
replica use the write-path lookup, while read-only replicas keep their
existing behavior of never deleting expired keys on read. Expiration on
replicas remains the master's responsibility, applied through the
propagated DEL, so the replica keyspace stays consistent with the
master.

Flags passed to the lookup functions are now derived once instead of
being recomputed at each call site, which removes the duplicated checks
and reduces the chance of the two paths drifting apart again.

Masters and standalone instances should see no change in behavior. The
goal is clearer code paths and fewer duplicated conditions, not a
change to any command's visible results.
