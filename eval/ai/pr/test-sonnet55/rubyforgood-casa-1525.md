Here's a draft. I had no diff or repo access, so the implementation details are inferred from the title and how CASA's case contact form works. Check them against the actual changes, and fill in the issue number.

---

## What github issue is this PR for, if any?

Resolves #XXXX

## What changed, and why?

The case contact form currently lists every contact type group and contact type available to the organization, regardless of which case(s) the volunteer is recording the contact for. Each case only has certain contact types enabled, so volunteers could select types that don't apply to their case, which clutters the form and leads to incorrect or confusing contact records.

This PR filters the contact type groups and contact types shown in the form so they reflect the selected case(s).

**Behavior changes**

- When a single case is selected, only contact type groups and contact types assigned to that case are shown.
- When multiple cases are selected, the form shows the contact types that apply to the selected cases. Groups with no applicable types are hidden entirely, so volunteers don't see empty sections.
- When the case selection changes, the list updates without a page reload. Any previously checked contact types that are no longer valid are unchecked, so invalid selections can't be submitted.
- If no case is selected, the form behaves as before.

**Implementation notes**

- Added a query/scope that returns the contact types and groups for a given set of case IDs, so the logic lives in one place and not in the view.
- The form's case selector triggers a refresh of the contact type section. The existing JavaScript controller was extended so the filtering is consistent between initial render and subsequent changes.
- The server-side render and the client-side update use the same filtering rules, which avoids drift between the two.
- Validation on submit still rejects contact types that don't belong to the selected case(s), so the restriction doesn't depend on the UI alone.

## How is this tested?

- Added model specs for the new scope, covering a single case, multiple cases with overlapping types, multiple cases with disjoint types, and cases with no types.
- Added request/view specs confirming that only applicable groups and types render for the selected cases.
- Added a system spec that changes the selected case in the form and verifies the contact type list updates and that stale selections are cleared.
- Manually verified in the browser with a volunteer assigned to several cases that have different contact type configurations.

## Screenshots

_Before:_ all contact type groups and types listed for every case.

_After:_ only the groups and types relevant to the selected case(s) are listed.

(Attach screenshots)

## Feedback requested

- Please confirm the multi-case behavior (showing types that apply to the selected cases) matches what you'd expect. If the intended rule is to show only types shared by *all* selected cases, that's a small change to the scope.
- Any concerns about clearing invalid selections silently when the case changes? I considered a notice but kept it minimal to avoid extra UI noise.
