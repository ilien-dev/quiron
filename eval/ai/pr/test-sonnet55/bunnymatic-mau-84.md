## Summary

This PR replaces the existing serializer layer with [jsonapi-rb](https://github.com/jsonapi-rb/jsonapi-rb) (`jsonapi-serializable` and `jsonapi-renderer`), so API responses follow the JSON:API specification consistently.

## Changes

- Added `jsonapi-rails` to the Gemfile and removed the previous serializer gem.
- Rewrote each serializer as a `JSONAPI::Serializable::Resource` subclass, declaring `type`, `attributes`, and relationships explicitly.
- Updated controllers to render through `jsonapi:` / `jsonapi_serializable` rather than the old `render json:` calls.
- Added relationship and `include` support so clients can request related resources, avoiding extra round trips.
- Updated serializer and request specs to match the new document structure (`data`, `attributes`, `relationships`, `included`).

## Behavior changes

Response payloads change shape. Attributes now live under `data.attributes` instead of at the top level, and related records appear in `relationships` / `included`. Any consumer of the API, including the frontend, must be updated to read the new structure.

## Testing

- Full RSpec suite passes locally.
- Manually checked the main endpoints for correct `type`, `id`, attributes, and relationship linkage.
- Confirmed error responses still return the expected status codes.

## Notes for reviewers

- Start with the serializer classes, then the controller changes, and finally the specs.
- Please check that I haven't missed any endpoint still rendering the old format.
- Frontend adjustments will land in a follow-up PR, so this should be merged and deployed together with it, or the client changes should be gated.

## Rollout

No database migrations are required. Because this is a breaking change to the response format, coordinate the deploy with the frontend update.
