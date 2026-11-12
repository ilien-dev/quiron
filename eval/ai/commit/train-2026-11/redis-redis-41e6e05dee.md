Allow most CONFIG SET during loading, block some commands in async-loading (#9878)

Previously, CONFIG SET was rejected with a -LOADING error while the server was loading a dataset, because the command was not flagged as allowed in that state. This was overly restrictive. Operators often need to adjust settings while a long load is in progress, for example to change logging, tune replication buffers, or modify limits that would otherwise require a restart and a repeat of the load.

This change marks CONFIG SET (and the related CONFIG GET and other safe config subcommands) as permitted during loading. A small number of configs remain unsafe to change at that point, because they affect the loading process itself or touch state that is being rebuilt. Those configs are flagged and rejected with an explicit error when a client tries to modify them while loading is in progress.

The change also addresses async-loading, which is used by diskless replication with swapdb. In that mode the server keeps serving reads from the old dataset while a new one is loaded in the background, so clients can still execute commands against live data. Some commands are not safe to run in this window, because they could modify or inspect state that is about to be swapped out, or interfere with the temporary database being populated. These commands are now blocked while async-loading is active, returning a clear error instead of producing undefined or inconsistent behavior.

To support this, command flags are extended so that each command can declare whether it is allowed during loading and whether it is allowed during async-loading. The command table metadata and the generated JSON command definitions are updated accordingly, and the dispatch path in processCommand checks the new flags before executing.

Tests cover:
- CONFIG SET of permitted parameters succeeding while a load is in progress
- CONFIG SET of restricted parameters being rejected during loading
- Blocked commands returning an error during async-loading
- Normal behavior being unchanged once loading finishes

This keeps the server more manageable during long loads while preserving the safety guarantees that the loading and async-loading states depend on.
