## Summary

This PR adds a postprocessing step for PanNuke data and tests to help ensure the resulting masks are suitable for downstream analysis. It makes the processing workflow easier to use consistently and provides a foundation for detecting regressions as the dataset code evolves.

## Changes

- Add a postprocessing step to the PanNuke workflow.
- Add tests covering the expected behavior and output of the new step.
- Check that postprocessing works alongside the existing PanNuke data-loading workflow.

## Motivation

PanNuke provides images and nuclear annotations for computational pathology research. A consistent postprocessing step helps prepare those annotations for use in segmentation and classification workflows, while focused tests make the expected behavior easier to maintain.

## Validation

Run the PanNuke-related tests and confirm that the postprocessed outputs have the expected structure and values.

*Draft based on the PR title and the [existing PanNuke dataset implementation](https://github.com/Dana-Farber-AIOS/pathml/blob/master/pathml/datasets/pannuke.py); the actual diff and test results were unavailable.*
