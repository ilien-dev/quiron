I don't have access to the branch or diff from this environment, so the details below are based on the title and the project's usual structure (Rails, Pundit policies, sv/en locales, Cucumber/RSpec). Bracketed items are placeholders to fill in before posting.

---

## Clues for admins to edit user profiles, accounts

**PivotalTracker story:** [link to story]

### Why

When an admin needs to update a member's information, it isn't obvious where to go. The user profile (name, member photo, contact details) and the user account (login email, password) are edited in different places. Neither page gives the admin any hint that editing is possible. Admins have been asking members to make changes themselves, or asking a developer where the edit form is. This PR adds clear, admin-only visual clues so the right edit action is easy to find.

### What changed

- **User show page:** Admins now see two distinct actions, **"Edit profile"** and **"Edit account"**, near the top of the page. Each has a short line of help text that explains what can be changed there. For example: *"Profile: name, photo, and contact information shown to other members"* and *"Account: login email and password."*
- **Users list (admin view):** Each row has small edit icons with tooltips. Admins can jump straight to the profile or account form without opening the user's page first.
- **Edit forms:** When an admin is editing someone else's profile or account, a notice banner at the top of the form says so (e.g. *"You are editing [member name]'s account as an admin"*). This reduces the risk of an admin confusing a member's account with their own.
- **Authorization:** All new links, icons, and banners are rendered only when the relevant policy permits it. Non-admin users see no change to their own pages.
- **I18n:** New strings are added to both `sv.yml` and `en.yml`. The Swedish wording follows the existing terminology for *profil* and *konto*.

### Screenshots

[Before / after: user show page]
[Before / after: users list]
[Admin editing banner]

### Testing

- New Cucumber scenarios cover:
  - an admin seeing and following the "Edit profile" and "Edit account" clues
  - a regular member not seeing the admin-only clues on another user's page
  - the admin banner showing on the edit forms
- View/policy specs were updated for the conditional rendering.
- The full test suite passes locally: [paste result / CI link].

### Notes for reviewers

- I kept profile and account editing as separate actions on purpose rather than merging them. They map to different forms and controllers, and the help text now explains the difference.
- Feedback on the Swedish copy is welcome, especially the help text wording, from anyone closer to how SHF admins describe these things.
- No database migrations are included.

---

If you can share the diff or the PivotalTracker story, I can tighten the "What changed" section to match exactly what the branch does.
