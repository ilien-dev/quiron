I didn't have the diff, so the Changes list below is a placeholder to match against the actual edits before you post it.

## Summary

This PR refreshes the license key documentation for MUI X so it matches how license keys are currently set up and validated. The existing pages had outdated wording and setup steps that no longer reflect current package behavior, which made it harder for users to know which key they need and where to add it.

## Changes

- Rewrote the introduction to explain what a license key is and which MUI X packages require one.
- Updated the setup instructions for installing and applying the key in an application.
- Clarified the license requirements for each plan tier.
- Refreshed the troubleshooting section, including the console messages users commonly see when a key is missing or invalid.
- Fixed broken links and removed references to pages that no longer exist.

## Notes for reviewers

Please check the code samples against the current package versions, and confirm the license terms wording against the source of truth before merging. This PR does not change any runtime code.

## Testing

[Describe how the changes were verified, for example a local docs build, a link check, and a review of the rendered pages.]
