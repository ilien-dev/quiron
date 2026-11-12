## Summary

This PR updates the data processing pipeline used to turn raw recorded player streams into the published MineRL dataset. The goal is to make the pipeline easier to run end to end and more reliable when processing large batches of recordings.

## Changes

- Restructures the pipeline stages (merge, render, generate, publish) so each can be run independently and resumed after a failure
- Improves handling of corrupt or incomplete recordings: they are now skipped and logged instead of aborting the run
- Cleans up path and configuration handling so input and output directories are set in one place
- Adds clearer progress and error logging across stages
- Removes dead code and unused helpers

## Testing

- Ran the full pipeline on a sample of recordings and confirmed the output matches the expected format
- Verified that existing data loaders read the generated data without changes

## Notes for reviewers

No changes to the public API or to the dataset format are intended. Please flag any stage whose behaviour differs from what you expect on your own data.
