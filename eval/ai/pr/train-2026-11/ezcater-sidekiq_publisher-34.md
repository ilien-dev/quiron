## Summary

Until now, the publisher process had no explicit handling for `INT` or `TERM`. When a deploy, autoscaler, or developer stopped the process, Ruby raised `Interrupt` or `SignalException` wherever execution happened to be. That could happen mid-batch, after jobs were pushed to Redis but before they were marked as published in Postgres. On restart, those jobs were published again, and the process exited with a noisy backtrace instead of a clean shutdown.

This PR traps `INT` and `TERM` and turns them into a cooperative shutdown request.

## Changes

- Signal handlers set a shutdown flag. They do no other work, which keeps them async-signal-safe and avoids acquiring locks or touching the database from inside a trap context.
- The runner checks the flag between iterations of its listen/publish loop. When the flag is set, it finishes the batch in progress, stops listening on the Postgres notification channel, releases its connection, and exits with status `0`.
- The blocking wait on notifications now uses a timeout, so a shutdown request is noticed promptly even when no new jobs arrive.
- A log line is emitted when shutdown begins and another when it completes, which makes stop behavior visible in production logs.

## Testing

- Added specs that send `TERM` and `INT` to a running publisher and assert that in-flight jobs are fully published and none are duplicated.
- Verified manually with `Ctrl-C` locally and with `kill -TERM` against a running process.

## Notes

No configuration changes are required. Existing deployments get the new behavior automatically.
