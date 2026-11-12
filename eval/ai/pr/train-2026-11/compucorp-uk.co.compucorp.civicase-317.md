I don't have the diff or the ticket, so this follows Compucorp's usual PR template and keeps the specifics generic. Anything in [brackets] needs checking against the actual change.

---

## Overview

This PR adds a **Reviews** tab to the Case details screen in CiviCase, so staff can see and manage all reviews linked to a case in one place. Previously, review activities were mixed in with the general activity feed, which made them hard to find and track.

## Before

- Review activities appeared only in the Activities tab, alongside every other activity type.
- There was no dedicated view for reviewing a case's review history or status.

## After

- The case details page has a new **Reviews** tab next to the existing tabs.
- The tab lists all review activities for the case, showing [type, status, reviewer, date].
- The tab is only displayed when the case type has review activities [or when the user has permission to view them].
- Empty state: a short message is shown when the case has no reviews.
- The tab respects existing case permissions and activity ACLs.

## Technical Details

- Registered the new tab through the case details tab configuration, following the pattern used by existing tabs.
- Added an Angular component, `civicaseReviewsTab`, with its template and styles, in the existing `ang/civicase` module.
- The component loads data through the existing `crmApi` activity query, filtered by case ID and review activity types, so no new API endpoints were needed.
- Added the tab's SCSS to the existing stylesheet and rebuilt the compiled CSS.
- Added Karma/Jasmine unit tests covering tab visibility, data loading and the empty state.

## Core overrides

None.

## Testing

1. Open a case whose type includes review activities and confirm the **Reviews** tab appears.
2. Check that the listed reviews match those in the Activities tab.
3. Open a case with no reviews and confirm the empty state is shown.
4. Log in as a user without permission to view the activities and confirm they are hidden.

## Comments

Pagination and filtering inside the tab are out of scope and can be added in a follow-up if needed.

---

If you share the diff or the ticket's acceptance criteria, I can replace the bracketed parts and the assumed details with the real ones.
