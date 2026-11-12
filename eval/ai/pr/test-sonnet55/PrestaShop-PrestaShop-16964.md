## Description

| Questions | Answers |
|---|---|
| Branch? | develop |
| Description? | Refactors the UI kit form theme and applies it to the Performance page |
| Type? | refacto |
| Category? | BO |
| BC breaks? | no |
| Deprecations? | no |
| Fixed ticket? | Part of the UI kit migration effort |
| Related PRs | None |
| Sponsor company | Your company name, or leave blank for a community contribution |

### Summary

This PR refactors the UI kit form theme used in the back office and applies it to the Performance page (`Advanced Parameters > Performance`). The goal is to make the theme a consistent, reusable building block, and to prove it on a real page with several form types.

### What changed

- **Form theme cleanup:** The UI kit form theme is reorganised so that each block (labels, help text, errors, choice widgets, switches, collapsible sections) is defined once and reused instead of duplicated or overridden per page.
- **Simplified markup:** Redundant wrappers and ad-hoc CSS classes are removed. Block names follow a consistent convention, which makes them easier to extend.
- **Performance page:** The forms on this page (smarty, debug mode, optional features, CCC, media servers, caching, memcache) now render through the refactored theme rather than page-specific templates.
- **Templates:** Twig templates that duplicated form-row markup are removed or reduced to the page-specific parts.

### Why

The Performance page combines many field types and conditional sections, so it is a good test of whether the theme holds up. Moving it onto the shared theme removes duplicated markup and brings the page in line with the rest of the UI kit migration. Other pages can then adopt the same theme with less custom code.

### How to test

1. Open `Advanced Parameters > Performance`.
2. Check that every section renders correctly: Smarty, Debug mode, Optional features, CCC, Media servers, Caching.
3. Change values in each section, save, and confirm the success message and persisted values.
4. Trigger a validation error, such as an invalid media server domain, and confirm the error displays on the right field.
5. Toggle the caching switch and confirm the related fields show or hide as before.
6. Compare with `develop` to confirm there are no visual regressions, including in the responsive layout.
7. Spot-check one or two other pages that use the shared form theme (for example, Shop Parameters > General) to confirm nothing else changed.

### Notes for reviewers

- No functional changes are intended, only markup and theme structure.
- Please pay attention to the block names in the form theme, as they are the new extension points.
- Front-end assets are rebuilt as part of this PR. UI tests were run locally against the Performance page.
