## Description

This PR adds a link from the new Reports page to the legacy reports page, so admins who still rely on the older report views can reach them without hunting through the admin menu or typing the URL by hand.

Since the new Reports dashboard became the default, the legacy page has been hard to find, even though it still offers exports and breakdowns that some users depend on. The new link is placed in the Reports page header, labeled "View Legacy Reports," and points to the existing legacy reports screen. No legacy functionality is changed or removed.

## Affects

- Reports page header (UI only)
- No changes to report data, queries, or the legacy reports screen itself

## Testing Instructions

1. Go to **Donations → Reports** in the WordPress admin.
2. Confirm the "View Legacy Reports" link appears in the page header.
3. Click the link and confirm it opens the legacy reports page.
4. Confirm the link only appears for users with permission to view reports.

## Pre-review Checklist

- [ ] Acceptance criteria satisfied and marked in related issue
- [ ] Relevant `@since` tags included in DocBlocks
- [ ] Includes unit tests (if applicable)
- [ ] Self-review of code and UX completed
