Commit Message: config: distinct resource/transport API versions.

Additional Description:
Previously, a single API version governed both the xDS transport protocol (the discovery service endpoint and DiscoveryRequest/DiscoveryResponse types) and the version of the resources delivered over it. This made v2 to v3 migration all-or-nothing: a management server had to upgrade its transport and resource types at the same time.

This PR splits the two concepts:

- `ConfigSource.resource_api_version` selects the API version of the resources requested (for example, `envoy.config.cluster.v3.Cluster`).
- `ApiConfigSource.transport_api_version` selects the xDS transport endpoint and message version used to fetch them.

Both default to `AUTO`, which keeps existing behavior. Operators can now mix versions, such as serving v3 resources over the v2 transport, so control planes can migrate incrementally. Type URLs in requests are derived from the resource version, and the gRPC method is derived from the transport version.

Risk Level: Medium (touches all xDS subscription paths; default behavior unchanged)
Testing: Unit and integration tests covering each transport/resource version combination for SotW, delta and REST subscriptions.
Docs Changes: Updated xDS protocol and versioning docs.
Release Notes: Added.
