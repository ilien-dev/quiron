This PR changes the formatting workflow in LGoodDatePicker so it runs for every pull request instead of on every push to `master`. Moving formatting into the PR process brings style changes into review before the code reaches the main branch.

With the current approach, formatting happens after changes have already landed on `master`. Running it during pull requests makes the resulting adjustments visible alongside the proposed changes, giving contributors and maintainers an opportunity to review the formatted code before merging. It also reduces the need for formatting cleanup after a merge and helps keep the main branch consistently formatted.

The scope of this change is the workflow trigger: formatting becomes part of the contribution process. The intended outcome is earlier formatting feedback, clearer reviews, and fewer follow-up formatting changes on `master`. There are no intended changes to the library’s public API or runtime behavior.
