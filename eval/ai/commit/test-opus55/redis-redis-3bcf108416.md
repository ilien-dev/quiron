Change FUNCTION CREATE, DELETE and FLUSH to be WRITE commands instead of MAY_REPLICATE. (#9953)

The FUNCTION CREATE, DELETE and FLUSH subcommands were originally flagged
as `may-replicate`, the same flag used by commands like EVAL and PUBLISH
whose effect on the dataset is not known up front. That flag was chosen
because functions are not keys, so it seemed wrong to treat the commands
as writes to the keyspace.

That reasoning does not hold up. Functions are part of the dataset: they
are saved in the RDB, loaded on startup, propagated to replicas and AOF,
and a replica must hold the same set of functions as its master to
behave correctly. Any command that changes the function library changes
server state in a way that must be persisted and replicated. That makes
it a write command, with all the protections write commands get.

Leaving these commands as `may-replicate` caused several problems:

* They could run on a read-only replica. The replica's function library
  would then diverge from its master's, and the next full sync would
  silently drop the change.
* They were not rejected when the server is in a state that refuses
  writes, such as a failing background save (`-MISCONF`) or not enough
  connected replicas to satisfy `min-replicas-to-write`.
* FUNCTION CREATE was not subject to `maxmemory` / OOM rejection, even
  though it can allocate a lot of memory to compile and store a new
  library.

This commit flags CREATE, DELETE and FLUSH as `write`. CREATE is also
flagged `denyoom`, since it can grow memory usage. DELETE and FLUSH free
memory, so they stay allowed under OOM, just like DEL and FLUSHALL.
Read-only subcommands such as FUNCTION LIST, FUNCTION INFO and FUNCTION
STATS keep their current flags, as do FCALL and FCALL_RO. FCALL is
gated by the functions it runs, not by changes to the library.

Behavior changes visible to users:

* Running FUNCTION CREATE, DELETE or FLUSH against a read-only replica
  now returns a `-READONLY` error instead of succeeding locally.
* These commands are rejected with `-MISCONF` and `-NOREPLICAS` under
  the same conditions as any other write command.
* FUNCTION CREATE is rejected with `-OOM` when the server is over its
  `maxmemory` limit and eviction cannot free space.

Tests were added for the replica and OOM cases, and existing tests were
updated to match the new flags reported by COMMAND INFO.
