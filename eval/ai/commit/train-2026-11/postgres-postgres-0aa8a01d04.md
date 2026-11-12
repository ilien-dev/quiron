Extend the output plugin API to allow decoding of prepared xacts.

Logical decoding previously emitted changes only once a transaction had committed, so two-phase transactions were invisible to output plugins until COMMIT PREPARED. Extend the output plugin API with optional callbacks that let plugins decode a transaction at PREPARE time and handle its later resolution:

  - filter_prepare: decide whether a prepared transaction is decoded.
  - begin_prepare: start a decoded prepared transaction.
  - prepare: emit the PREPARE, including its GID and LSN.
  - commit_prepared and rollback_prepared: emit the final outcome.

Plugins that do not register these callbacks keep their existing behavior, and non-prepared transactions continue to use the begin and commit callbacks. The reorder buffer now retains the prepare-related state needed to replay a transaction from its PREPARE record and resolve it later, as long as the slot's restart LSN still covers it. Regression tests in contrib/test_decoding exercise the new callbacks.
