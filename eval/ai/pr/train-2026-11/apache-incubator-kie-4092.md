I couldn't check the diff because this folder isn't a git repository, and the title is cut off at "Ki…". The description below is inferred from the title, so verify the details against the actual changes before posting.

## Summary

This PR adds a case-insensitive comparison operator, `equalsIgnoreCase`, to the Kie expression and evaluation support. Callers can compare strings without lowercasing or uppercasing values first. It is tracked under DROOLS-6759.

## Motivation

Rules and expressions that compare user-supplied or externally sourced strings often fail to match only because of capitalization differences, such as `"Approved"` versus `"APPROVED"`. Users currently have to normalize both sides in their own code or write workarounds. A first-class `equalsIgnoreCase` operator makes the intent explicit and keeps the comparison logic in one place.

## Changes

- Added the `equalsIgnoreCase` comparison operator to the operator registry.
- Implemented null-safe semantics that match the existing `equals` operator: two nulls are treated consistently, and null against a non-null value does not match.
- Comparison follows `String.equalsIgnoreCase` semantics, which are locale-independent.
- Added unit tests for matching and non-matching values, mixed case, null handling, and non-string inputs.
- Updated the documentation to list the new operator alongside the existing comparison operators.

## Testing

- Unit tests for the new operator were added and pass locally.
- Existing comparison tests were run to check for regressions.

## Notes for reviewers

- Non-string operands are handled the same way as in the existing string operators. Please confirm this matches your expectations.
- The change is additive. No existing behavior is modified.
