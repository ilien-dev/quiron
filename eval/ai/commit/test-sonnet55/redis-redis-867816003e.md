Auto-generate the command table from JSON files (#9656)

Until now the command table lived as a hand-maintained array in `server.c`. Every command's name, arity, flags, key specs, and ACL categories were written out by hand in C. The documentation metadata (summary, complexity, history, arguments) lived in a separate place, in the redis-doc repository. The two sources drifted, adding a command meant editing several files, and the C table was easy to get subtly wrong.

This change makes one JSON file per command the single source of truth, and generates the C table from those files at build time.

## What changed

- Added `src/commands/*.json`, one file per command (or per subcommand). Each file describes the command's:
  - name, group, and `since` version
  - summary and complexity
  - arity, function name, and flags
  - ACL categories and command tips
  - key specs and history
  - argument tree
  - container/subcommand relationship

- Added `utils/generate-command-code.py`. It reads every JSON file under `src/commands/` and emits `src/commands.def`, which contains the `redisCommand` table plus the static arrays for arguments, history, tips, and key specs. The script validates its input and fails the build on malformed files, duplicate entries, or unknown fields.

- Removed the hand-written command table from `server.c`. The generated `commands.def` is included in its place, and the handler functions are referenced by name from the generated table.

- Updated `src/Makefile` so `commands.def` is regenerated whenever a JSON file or the generator changes. A normal `make` therefore needs Python available. The generated file is also committed, so building from a source tree without Python still works as long as the JSON files are unmodified.

- Moved the per-command documentation metadata into the server. Because the argument and history structures now exist at compile time, `COMMAND DOCS` can be answered from the same data that drives the command table, with no external lookup. `COMMAND INFO` and `COMMAND GETKEYS` read key specs from the same generated structures.

## Behavior

There is no intended change in command semantics. Arity, flags, ACL categories, and key specs should be identical to the previous hand-written table. Where the old table and the documentation disagreed, the JSON now holds a single reconciled value. Those fixes are limited to metadata and do not alter execution paths.

## Why this approach

- **One place to edit.** Adding or changing a command is now a JSON edit plus the C handler, so metadata can no longer diverge between the server and the documentation.
- **Machine-readable metadata.** Clients, docs tooling, and `COMMAND DOCS` consumers get structured data straight from the source, so they don't have to parse prose.
- **Compile-time tables.** The generated structures are `static const` data. There is no startup population cost, and subcommand tables are wired up by the generator rather than by runtime registration code.
- **Early validation.** Typos in flags, ACL categories, or argument types are caught at build time instead of surfacing as odd runtime behavior.

## Notes for contributors

When adding a command, create `src/commands/<name>.json`, implement the handler, and run `make`. Do not edit `commands.def` by hand, because the next build will overwrite it. Subcommands go in `<container>-<sub>.json` and name their container in the `container` field.

The generator needs only the Python standard library.
