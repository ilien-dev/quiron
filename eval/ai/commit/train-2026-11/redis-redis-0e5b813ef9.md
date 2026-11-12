Multiparam config set (#9748)

We can now do: `config set maxmemory 10m repl-backlog-size 5m`

## Basic algorithm to support "transaction like" config sets:

1. Backup all relevant current values (via get).
2. Run "verify" and "set" on everything, if we fail run "restore".
3. Run "apply" on everything (optional optimization: skip functions
   already run). If we fail run "restore".
4. Return success.

### restore

1. Run set on everything in backup. If we fail log it and continue
   (this puts us in an undefined state but we decided it's better than
   the alternative of panicking). This indicates either a bug or some
   unsupported external state.
2. Run apply on everything in backup (optimization: skip functions
   already run). If we fail log it (see comment above).
3. Return error.

## Implementation/design changes:

* Apply functions are idempotent (have no effect if they are run more
  than once for the same config).
* No indication in set functions if we're reading the config or running
  from the `CONFIG SET` command (removed the `update` argument).
* A set function should set some config variable and assume an
  (optional) apply function will use it later to apply the change. If
  we know a setting can be safely applied immediately, can always be
  reverted and doesn't depend on any other configuration, we can apply
  it immediately from within the set function (and not store the
  setting anywhere). This is the case for the `dir` config, for
  example, which has no apply function. No apply function is needed
  either when setting the variable in the `server` struct is all that
  is required for the configuration to take effect. Note that the
  original concept of `update_fn`, which received the old and new
  values, was removed and replaced by the optional apply function.
* Apply functions use settings written to the `server` struct and don't
  receive any inputs.
* For the generic (non-special) configs, if the value doesn't change we
  avoid calling the setter (possible future optimization: avoid calling
  the apply function as well).
* Passing the same config parameter more than once to `config set`
  fails. You can't do `config set my-setting value1 my-setting value2`.
  The same applies to a config and one of its aliases.
* Each distinct apply function is called only once per `config set`
  invocation, even when several of the given parameters share it
  (e.g. multiple TLS-related configs are applied together).

Note that getting `save` to work here as before in the context of
config file parsing was a pain. The config file supports an aggregate
`save` definition, where each `save` line is appended to the server's
save params. This is unlike any other line in the config file, where
each line overwrites any previous configuration. Since we now support
passing multiple save params in a single line (see the top comments
about `save` in #9644), we should deprecate the aggregate nature of this
config line and perhaps remove this ugly code in the future.

Tests were added to cover setting multiple parameters at once,
rejecting duplicate parameters, and verifying that a failure in one
parameter's set or apply stage rolls back all the other parameters
given in the same command to their previous values.
