## Summary

This PR removes the provider-imposed requirements that were previously pinned in `setup.cfg`. Airflow core should not carry dependency constraints that exist only because a particular provider needs them. Those requirements belong to the providers themselves, and keeping them in core couples the two in a way that makes upgrades and dependency resolution harder than necessary.

## Changes

- Removed provider-specific requirements from the `install_requires` and extras sections of `setup.cfg`.
- Left only the dependencies that Airflow core actually needs to run.
- Relied on each provider's own package metadata to declare what it requires.

## Motivation

Previously, installing Airflow core could pull in or constrain packages that were irrelevant unless a specific provider was installed. This produced unnecessary version conflicts and made the core dependency set harder to reason about. Moving the responsibility to providers keeps core lean and lets providers evolve their requirements independently.

## Impact

- Users who install providers continue to receive the dependencies those providers need, via the provider packages.
- Users who install only core no longer receive provider-driven constraints.
- No runtime behavior of core changes.

## Testing

- Verified a clean install of core resolves without the removed requirements.
- Verified providers still install with their declared dependencies.
- Existing CI checks pass.
