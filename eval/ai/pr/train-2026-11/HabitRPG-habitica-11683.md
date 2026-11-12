## Summary

This PR fixes several issues that prevent the local Docker development setup from running smoothly for contributors.

## Changes

- Corrects service configuration so the Habitica app and its supporting containers start and connect reliably.
- Fixes environment variable defaults and volume mounts used during local development.
- Updates the local Docker setup documentation so the steps match the current configuration.

## Why

Contributors following the existing guide could hit startup failures and connection errors when running the stack locally. These changes make the default Docker workflow work without manual workarounds.

## Testing

- [ ] `docker compose up` starts all services without errors
- [ ] The web client loads at the expected local address
- [ ] The API responds to requests
- [ ] Data persists across container restarts

## Notes

This PR does not change production configuration or application logic.

---

I wrote this from the title alone because the working directory isn't a git repository, so I couldn't read the diff. Replace the change bullets with the specifics from your commits, and only check the testing boxes you've actually run.
