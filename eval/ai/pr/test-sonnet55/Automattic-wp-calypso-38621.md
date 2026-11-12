## Proposed Changes

* Adds a dedicated error view to the site migration flow, shown when a migration fails or cannot be started.
* Replaces the generic fallback with a clear message explaining that something went wrong, plus actions the user can take next (try again, or contact support).
* Wires the error view into the migration step container so failures from the migration status check and the start-migration request both route to it.
* Adds tracks events for when the error view is displayed and when users click retry or contact support, so we can see how often and why migrations fail.
* Adds unit tests covering rendering, button handlers, and the routing from failure states.

## Why are these changes being made?

Right now, when a site migration fails, users land on a blank or generic screen with no explanation and no way forward. That's a frustrating dead end at a high-stakes moment, since they're trusting us with their site. A clear error state with next steps should reduce abandoned migrations and support confusion, and the analytics will tell us where failures concentrate.

## Testing Instructions

1. Check out this branch and run `yarn start`.
2. Start a site migration from `/setup/site-migration`.
3. Force a failure, for example by blocking the migration request in DevTools or using an invalid source URL.
4. Confirm the error view appears with the retry and contact support actions.
5. Click **Try again** and verify the flow restarts at the right step.
6. Click **Contact support** and verify the help link opens.
7. Check that the tracks events fire for each interaction.
8. Run `yarn test-client client/landing/stepper` and confirm tests pass.

## Pre-merge Checklist

- [ ] Tested on desktop and mobile viewports
- [ ] Copy reviewed for tone and translatability
- [ ] Accessibility checked (focus, heading order, screen reader)
