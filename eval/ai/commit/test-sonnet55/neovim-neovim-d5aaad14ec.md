Followup improvements to LSP (#11430)

Address review feedback and rough edges left over from the initial
LSP client work.

- Make client shutdown more robust: send `shutdown` and `exit`
  in order, and stop the RPC process cleanly even if the server
  never replies.
- Fix handling of buffer-local state so that detaching a buffer
  from a client no longer leaves stale diagnostics or
  autocommands behind.
- Normalize position and range conversion between Neovim's
  0-based byte indexes and the UTF-16 offsets used by the
  protocol, fixing off-by-one errors on lines with multibyte
  characters.
- Improve error reporting: surface server errors and invalid
  responses through consistent log messages instead of failing
  silently or raising Lua errors in callbacks.
- Tidy the default handlers for hover, definition and
  references so they respect empty results.
- Expand the test suite to cover shutdown, buffer detach and
  multibyte edits, and update the docs to match.
