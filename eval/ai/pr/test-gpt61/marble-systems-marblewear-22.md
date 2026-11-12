I couldn’t access the repository or PR diff, so this draft is based on the title. Implementation details and test results should be confirmed before posting.

## Summary

This PR consolidates the components used by `ProductOverview` and updates the data rendered in the product overview experience. It brings the component structure and displayed information into alignment, making the view easier to understand, maintain, and extend.

The change addresses two related concerns: how the overview is assembled and what information it presents. Consolidating components creates a clearer structure for the page, while updating the rendered data ensures that the overview reflects the intended product information. Together, these changes establish a more cohesive foundation for future work on the product experience.

## Component consolidation

The component changes focus on bringing related presentation responsibilities together within `ProductOverview`. The intent is to make the relationship between the overview and its supporting components easier to follow, with clearer boundaries around where product information is prepared and displayed.

This structure should make future updates more straightforward. When the overview needs a layout adjustment or a change to displayed content, contributors should be able to identify the relevant component more easily and understand how their changes affect the rest of the view.

Review should focus on whether the consolidated structure preserves the necessary behavior of the existing components and whether their responsibilities remain clear. Particular attention should be given to how data moves through the component hierarchy and whether the resulting interfaces are appropriate for the information each component renders.

## Updated rendered data

The data changes update the information presented by `ProductOverview`. This work should be reviewed alongside the component consolidation, since a structural change can also affect how values are passed, selected, and displayed.

The key review question is whether each visible value corresponds to the intended product data. Labels, formatting, and conditional rendering should remain understandable across the product records supported by the application. Where information is optional, the overview should handle its absence without introducing confusing gaps or displaying unintended values.

These updates also provide an opportunity to check consistency across the overview. Related pieces of information should use compatible presentation patterns so that users can scan and interpret the product details with confidence.

## Validation and review

Validation should cover both the component changes and the resulting user experience:

- Compare the overview before and after the change to identify unintended differences in content, layout, or behavior.
- Verify that displayed values match the underlying product record.
- Check representative products with different combinations of available data.
- Confirm that missing or optional values are handled appropriately.
- Exercise any existing interactions affected by the consolidated components.
- Run the repository’s applicable lint, type, build, and test checks.

Reviewers should assess the structural changes and data changes together. A successful outcome is an overview whose component organization is easier to maintain and whose displayed information matches the intended product data.

## Testing status

Test execution and results have not been supplied for this draft. Replace this section with the checks performed, their outcomes, and any known limitations before the PR is ready for review.
