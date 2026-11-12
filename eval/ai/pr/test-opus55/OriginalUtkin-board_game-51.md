## Implement drag and drop mechanic for a card

### Summary

This PR adds drag and drop support for cards, so players can pick up a card from their hand and place it onto a valid area of the board. It makes card play direct and tactile instead of relying on click-to-select.

### Changes

- **Draggable card component:** Cards respond to pointer down, move and up events. While dragging, the card follows the cursor with a slight lift (scale and shadow) for visual feedback.
- **Drop zones:** Board slots are registered as drop targets. Each zone checks whether the dragged card can be placed there and highlights itself when hovered with a valid card.
- **Snap and return behavior:** A card dropped on a valid zone snaps into position and updates game state. A card dropped elsewhere animates back to its original place in the hand.
- **State handling:** Drag state is kept separate from game state, so a cancelled drag never leaves the board inconsistent.

### Testing

- Dragged cards onto valid and invalid zones and confirmed correct snapping and return animations.
- Verified that rapid or interrupted drags (releasing outside the window, for example) reset cleanly.
- Checked that existing card interactions still work as expected.

### Notes

Touch input support and keyboard accessibility for card placement are not part of this PR and can be handled in a follow-up.

---

I don't have access to the branch here, so I based this on the title. Change the specific bullets (component names, touch support, tests) to match what the code does.
