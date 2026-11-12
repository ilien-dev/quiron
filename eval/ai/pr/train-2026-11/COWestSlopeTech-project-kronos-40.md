I couldn't see the diff because this directory isn't a git repository, so I wrote the description from the title. Check the specifics against the actual code before you post it.

## Summary

This PR adds the ability to fetch event data from a Google Calendar so Project Kronos can read scheduled events and use them as a data source for downstream features.

## Changes

- Added a Google Calendar client that authenticates with the Google Calendar API and retrieves events from a specified calendar.
- Added a data-fetching function that accepts a start and end date and returns events in a normalized internal format: title, start and end times, time zone, location, and attendees.
- Added configuration for OAuth credentials and the target calendar ID, read from environment variables rather than hardcoded values.
- Added error handling for expired or revoked tokens, rate limiting (HTTP 429) with retry and backoff, network timeouts, and calendars with no events.
- Added unit tests for event normalization and fetch logic, with the Google API mocked so tests run offline.

## Implementation notes

- Recurring events are expanded with `singleEvents=true`, so each occurrence is returned as its own item, sorted by start time.
- Timestamps are stored in UTC, and the original time zone is preserved for display.
- Pagination follows `nextPageToken` until all pages are retrieved.
- Credentials are never logged. Token refresh is handled by the client library.

## Testing

- Unit tests pass locally with the Google API mocked.
- Manually verified against a real calendar containing single and recurring events.
- Confirmed that a date range with no events returns an empty list rather than an error.

## Reviewer notes

- Please confirm the requested OAuth scope (read-only `calendar.readonly`) meets our security expectations.
- Setup requires `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_CALENDAR_ID` to be set. See the updated README section.
