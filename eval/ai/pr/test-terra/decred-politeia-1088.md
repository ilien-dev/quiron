Add a v2 `StartVote` API that binds an administrator’s signature to the full set of vote parameters. In v1, the signature covered only the proposal token; v2 signs the hex-encoded SHA-256 digest of the JSON-encoded `Vote` structure.

The v2 vote includes the proposal version and vote type alongside the existing voting parameters. Including the proposal version in the signed data identifies the revision being put to a vote. The vote type provides a way to distinguish voting processes as Politeia adds support for additional proposal workflows. [API reference](https://pkg.go.dev/github.com/decred/politeia%40v1.5.0/politeiawww/api/www/v2)

The request continues to specify the vote mask, duration, quorum and approval percentages, and available options. Together, these fields describe the ballot and the conditions for approval. Signing the complete structure makes those settings part of the administrator’s signed request.

The v2 reply also updates the block-height fields: `StartBlockHeight` and `EndBlockHeight` are unsigned integers, and the latter replaces the v1 `EndHeight` name for consistency. The reply retains the start block hash and the list of eligible tickets.

Clients using the v2 route must construct and sign the v2 vote payload and decode the updated reply types. Consumers of stored vote data should account for the proposal version and vote type when interpreting a v2 vote. This change establishes the API representation needed to identify both the proposal revision and the voting process associated with a vote.

*Draft based on the published v2 API documentation; I could not verify the pull request’s full diff.*
