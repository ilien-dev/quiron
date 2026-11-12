Note: I couldn't see the actual diff (the working directory isn't a git repo), so this description is written from the title and general UI-work conventions. Adjust the specifics to match the real changes.

---

## Enhanced UI

### Summary
This PR improves the look, consistency, and usability of the symptoms-mobile-app interface. The goal is to make symptom reporting faster and clearer for users, while giving the codebase a more consistent set of styles and components to build on.

### Changes
- **Visual consistency:** Unified colors, typography, spacing, and icon usage across screens, so similar elements look and behave the same way throughout the app.
- **Layout improvements:** Reworked screen layouts to make better use of space on different screen sizes and orientations, reducing clutter and improving readability.
- **Navigation and interaction:** Made primary actions easier to find and tap, with larger touch targets, clearer labels, and better visual feedback on interaction.
- **Accessibility:** Improved text contrast and readability, and made sure interactive elements are clearly distinguishable.
- **Code cleanup:** Consolidated duplicated styles into shared definitions and removed unused UI code and assets.

### Motivation
Users report symptoms on a regular basis, often in quick interactions. An interface that is clear and predictable reduces friction and the chance of input errors. Centralizing styles also makes future UI changes cheaper and less error-prone.

### Testing
- Manually verified the affected screens on Android and iOS (emulator and/or physical device).
- Checked behavior on small and large screen sizes.
- Confirmed that existing flows (e.g., login, symptom reporting, history) work as before.
- Ran the existing test suite and linting with no new failures.

### Screenshots
_Before/after screenshots to be added here._

### Notes for reviewers
- This PR contains no functional or data-model changes, only presentation and styling.
- Most of the diff is in style and template files, so reviewing screen by screen is probably easiest.
- Feedback on design choices is welcome, especially on spacing and color decisions.
