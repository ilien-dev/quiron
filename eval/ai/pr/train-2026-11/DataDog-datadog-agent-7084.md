## What does this PR do?

Stops writing API keys to disk when the forwarder serializes transactions to retry files.

When the intake is unreachable, the forwarder stores pending transactions on disk so they can be retried later. Each serialized transaction currently includes its HTTP headers and endpoint, which contain the plaintext `DD-API-KEY`. This PR removes the API key from the serialized payload. In its place, the PR stores a reference to the domain and key index. On deserialization, the key is resolved again from the current configuration.

## Motivation

Retry files can persist on the host for a long time. They may also be picked up by backups, flares, or support bundles. Storing credentials in them increases the risk of leaking keys. It also means rotated or revoked keys can resurface on retry.

## Additional Notes

- Retry files written by older Agent versions are still readable. Any embedded key is ignored in favor of the configured one.
- If the referenced key no longer exists in the configuration, the transaction is dropped and a warning is logged.

## Describe how to test/QA your changes

Block the intake endpoint and let retry files accumulate. Confirm that no API key appears in the files, then restore connectivity and verify the transactions are sent successfully.

---

I wrote this without access to the actual diff. Please adjust the implementation details, especially the key-reference mechanism and the backward-compatibility behavior, to match the code.
