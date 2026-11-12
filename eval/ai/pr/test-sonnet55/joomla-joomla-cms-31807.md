### Summary of Changes

This PR normalizes the filters used in the Contacts component, both in the backend list view and in the content plugin's modal (xtd-contact) used from the editor button.

Previously, the filter forms and the list model handling for contacts differed between the backend and the modal. This caused inconsistencies in the available filter fields, their naming and how their state was populated and stored.

This PR aligns them by:

- Using the same filter fields (search, published, category, access, language, etc.) in both the backend and the modal.
- Making the modal's filter form consistent with the backend `filter_contacts.xml`.
- Updating the model's `populateState` / `getListQuery` so both views use the same filter keys.
- Adjusting the layouts so the filter bar renders the same way in both places.

### Testing Instructions

1. Apply the patch (or build the PR).
2. Go to **Components → Contacts** in the administrator and check that all filters work: search, status, category, access, language, and featured where available.
3. Open an article in the editor and click the **Contact** button to open the modal.
4. Verify the same filters appear and work in the modal.
5. Clear the filters and confirm the lists reset correctly in both views.

### Expected Result

Filters look and behave identically in the backend list and in the modal, and selected values persist consistently.

### Actual Result (before patch)

Filters differ between the two views, and some are missing or do not work in the modal.

### Documentation Requirements

None. No new features, only internal consistency.

### Backward Compatibility

No B/C breaks are expected.
