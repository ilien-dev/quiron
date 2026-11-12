## Proposed changes

The FileViewer context menu and hotkeys for partial staging were inconsistent depending on where the viewer was hosted (commit dialog, diff tab, stash, file history). The same action appeared under different names, and some entries were shown in contexts where they could not work.

This PR makes the FileViewer use "Stage lines" / "Unstage lines" / "Reset lines" consistently:

- Unify the menu item texts so the same action has the same label in every host form.
- When nothing is selected, the action applies to the line at the caret; with a selection, it applies to the selected lines. The label no longer changes between these cases.
- Show the items only when the action is supported for the displayed diff (worktree or index changes), instead of showing disabled or non-functional entries.
- Keep the hotkeys (`S` for stage/unstage, `R` for reset) aligned with the menu items, so that a key does exactly what the visible menu entry does.
- Reset still asks for confirmation before discarding changes.

No change to the patch creation logic itself; this is limited to how the commands are presented and enabled.

## Screenshots

### Before

<!-- context menu in commit dialog / diff tab -->

### After

<!-- context menu in commit dialog / diff tab -->

## Test methodology

- Manual: staged, unstaged and reset single lines and selections in the commit dialog and in the diff tab for worktree and index.
- Existing unit and integration tests pass.

## Merge strategy

I agree that the maintainer squash merge this PR (if the commit message is clear).
