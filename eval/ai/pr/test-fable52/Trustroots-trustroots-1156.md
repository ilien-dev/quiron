## Refactor OfferLocation React map

### What

This PR refactors the `OfferLocation` component, which renders the small map on a member's profile showing where their hosting or meeting offer is located. Behaviour is intended to stay the same; the goal is to make the component easier to read, test and reuse.

### Why

`OfferLocation` had grown to mix several concerns in one place: viewport state, map style selection, marker rendering and zoom handling. That made it awkward to change any of them without touching the others, and it duplicated logic that already exists in our other React maps. Cleaning this up now reduces the cost of upcoming map work and brings the component in line with the rest of the migrated React code.

### Changes

- Convert `OfferLocation` to a function component using hooks, with viewport state kept in a single `useState` call.
- Extract the marker and approximate-location circle into their own small presentational components, so the decision of which to show lives in one place.
- Reuse the shared map style and layer helpers instead of defining them locally.
- Move zoom limits and default zoom into named constants rather than inline numbers.
- Tidy up `propTypes` so that `location` and `offer` are validated explicitly, and remove props that were no longer read.
- Remove dead code and unused imports left over from the Angular migration.
- Add unit tests covering the exact-marker and approximate-circle cases and the default viewport.

### What has not changed

- The public props of the component, so existing callers need no changes.
- Privacy behaviour: other members' offers still render as an approximate area, and the exact marker is only shown where it was shown before.
- Map styles, attribution and tile sources.

### Testing

- `npm run test:client` passes locally, including the new tests.
- `npm run lint` passes.
- Manually checked in the browser:
  - Own profile with a hosting offer
  - Another member's profile with a hosting offer
  - A profile with a meet offer
  - A profile with no offer, where the map should not render
  - Zooming and panning on desktop and at a narrow mobile width

### Notes for reviewers

The diff is easiest to read commit by commit: the conversion to hooks comes first, then the extraction of the sub-components, then the tests. The first commit is a mechanical change and should have no functional effect.

If you spot any visual difference from the current map, such as the circle radius, default zoom or marker position, please flag it, as that would be an unintended regression.

### Screenshots

_Before and after screenshots to be added._
