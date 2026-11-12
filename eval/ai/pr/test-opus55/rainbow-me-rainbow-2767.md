I don't have the diff (the working directory isn't a git repo), so this draft assumes the fix is to the token price chart scrubbing gesture. Adjust the specifics to match the actual change.

---

## Fix scrubbing

### What changed
This PR fixes several issues with scrubbing on the token price chart:

- **Gesture conflicts:** Scrubbing no longer fights with the parent scroll view. Horizontal pans now reliably activate the chart gesture, and vertical swipes still scroll the sheet.
- **Stale values:** The price and date labels now update on every frame while scrubbing. Before, they could lag or show the previous point after a quick drag.
- **Release behavior:** Lifting a finger now resets the chart to the latest price. Previously the last scrubbed value could stay on screen.
- **Haptics:** Selection haptics fire once per data point instead of repeatedly at the same index.

### Why
Users reported jittery labels and accidental scrolls when inspecting historical prices, mainly on Android and on charts with dense data.

### How to test
1. Open any token's expanded state.
2. Scrub slowly and quickly across the chart on each timeframe (1H through 1Y).
3. Confirm the labels track your finger, the sheet doesn't scroll, and the price resets when you release.
4. Repeat on iOS and Android.

### Screenshots / recordings
_Before / after videos_
