## Description

This PR adds client-side encryption support to the Cosmos DB .NET SDK using customer-provided keys. Sensitive properties in documents can now be encrypted before leaving the client and decrypted on read, so the service never sees plaintext values.

### Changes

- Introduces an encryption policy on containers that specifies which paths are encrypted and the algorithm/key used for each.
- Adds a key-provider abstraction so customers can supply their own data encryption keys (for example, wrapped by a key store such as Azure Key Vault).
- Encrypts and decrypts payloads transparently in the item CRUD, query, and change feed request paths.
- Adds a configuration option on the client builder/options to enable encryption and register the key provider.
- Includes unit and emulator tests covering encryption round trips, queries on encrypted properties, and key rotation scenarios.

### Behavior notes

- Encrypted properties are stored as ciphertext, so server-side filtering on them is limited to supported query patterns.
- Existing unencrypted containers are unaffected unless a policy is configured.

### Testing

- New unit tests pass locally.
- Emulator tests added for end-to-end validation.
