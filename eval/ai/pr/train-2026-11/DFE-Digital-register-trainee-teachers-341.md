I couldn’t access the pull request’s changes, so this draft is based on the title and needs checking against the diff:

This PR introduces custom email validation for Register trainee teachers, giving the service explicit control over how email addresses are checked and how validation failures are presented to users.

The aim is to catch invalid addresses when they are entered and provide clear feedback so users can correct them before continuing. Keeping these rules in a dedicated validator also makes the expected behaviour easier to understand, maintain and reuse wherever the same requirements apply.

Review should focus on which email fields use the validator, the formats it accepts and rejects, and whether error messages give users enough information to resolve a problem. Blank values should be checked against the relevant field’s existing requirements, while valid addresses should continue through the form as expected.

Suggested verification includes submitting valid and malformed addresses, checking required and optional fields, and confirming that errors appear correctly alongside other form validation messages. Automated coverage should capture the agreed acceptance rules and relevant edge cases to help prevent regressions as the service evolves.
