I don't have the branch diff in this workspace, so this draft is based on how the starter is structured (Gravity Forms over WPGraphQL, with Formik and Yup on the front end). Please check the file paths and details against the actual changes before you post it.

---

## Feature/45: Form Handling

Closes #45

### Summary

This PR adds end-to-end form handling to the starter. Forms built in the WordPress admin with Gravity Forms can now be queried through WPGraphQL, rendered as React components, validated on the client, and submitted back to WordPress. Editors can build and change forms in WordPress without touching the front end.

### What's Changed

**Data layer**
- Added GraphQL fragments and queries for Gravity Forms, using the WPGraphQL for Gravity Forms plugin. The queries fetch form metadata, field definitions, validation rules, and confirmation settings.
- Added a form query partial so forms embedded in post or page content resolve along with the rest of the page data at build time.
- Added a submission mutation that sends field values and returns either a confirmation or field-level errors.

**Components**
- Added a `GravityForm` organism that takes a form object from WordPress and renders its fields in order.
- Added field components for the common Gravity Forms field types:
  - Text, Email, Phone, Website
  - Textarea
  - Select and Multi-select
  - Checkbox and Radio
  - Name and Address (compound fields)
  - Hidden
- Field components follow the existing atomic design structure and use shared input, label, and error-message atoms where possible.
- Unsupported field types fall back to an empty render and log a warning in development, so one unmapped field doesn't break the page.

**Validation and state**
- Form state is managed with **Formik**.
- Validation schemas are built at runtime with **Yup**, using each field's settings from Gravity Forms (required, max length, email format, and so on). The front end applies the same rules the editor set in WordPress.
- Server-side validation errors returned by the mutation are mapped back onto the matching fields, so users see one consistent error display whether the error came from the client or from WordPress.

**Submission flow**
- Submissions go through a Next.js API route instead of calling WordPress directly from the browser. This keeps the WordPress GraphQL endpoint and any credentials on the server.
- After a successful submission, the form shows the confirmation message configured in Gravity Forms. Redirect-type confirmations are also supported.
- Loading and disabled states are applied while a submission is in flight to prevent double-submits.

**Gutenberg integration**
- The Gravity Forms block is registered in the block renderer, so forms added through the block editor render automatically.

### How to Test

1. Make sure Gravity Forms and WPGraphQL for Gravity Forms are installed and active on your WordPress backend.
2. Create a form that includes several field types, with some fields marked as required.
3. Add the form to a page using the Gravity Forms block.
4. Run `npm run dev` and open the page.
5. Check that:
   - All fields render with the correct labels, placeholders, and descriptions.
   - Submitting with required fields empty shows inline errors.
   - Invalid input, such as a malformed email, is caught before submission.
   - A valid submission shows the configured confirmation message.
   - The entry appears under **Forms → Entries** in WordPress.

### Notes

- The required plugins are listed in the README. A missing plugin will cause the form queries to fail.
- File upload, CAPTCHA, and multi-page forms are out of scope for this PR and will be handled in follow-up issues.
- Styling is kept minimal and uses the existing Tailwind setup so projects built on the starter can theme forms easily.

### Checklist

- [ ] Tested locally against a WordPress instance with Gravity Forms
- [ ] Storybook stories added for new field components
- [ ] Linting and formatting pass
- [ ] README updated with plugin requirements

---

If you paste the diff or the list of changed files, I can tighten this to match exactly what the branch contains.
