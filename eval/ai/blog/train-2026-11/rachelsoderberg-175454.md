# Update Salesforce Fields With A Button Click (Salesforce Classic)

Sometimes a user just needs to move a record to the next step. Maybe an Opportunity needs to go from "Proposal" to "Closed Won," or a Case needs its status set to "Escalated." Editing the record, scrolling to the field, changing the value, and saving takes time, and users skip steps when the process is tedious.

In Salesforce Classic, you can add a custom button to the detail page that updates a field in one click. This post walks through building one with JavaScript.

## When to Use This Approach

A button with JavaScript works well when:

- The update is a single field change or a small set of changes.
- Users work in Salesforce Classic, or your org hasn't moved to Lightning Experience yet.
- You need the update to happen without opening an edit page.

If your org runs Lightning Experience, use a Quick Action or a Flow instead. Classic buttons with "Execute JavaScript" don't run in Lightning.

## Prerequisites

You need:

- Permission to customize objects and page layouts (System Administrator or equivalent).
- Read and edit access to the target field for the users who will click the button.
- The API name of the field you want to update. For this example, we'll use `StageName` on Opportunity.

## Step 1: Create the Custom Button

1. Go to **Setup**, then **Object Manager**, and select your object (for example, Opportunity).
2. Click **Buttons, Links, and Actions**, then **New Button or Link**.
3. Fill in the fields:
   - **Label:** Mark as Closed Won
   - **Name:** Mark_As_Closed_Won
   - **Description:** Sets the stage to Closed Won and refreshes the page.
   - **Display Type:** Detail Page Button
   - **Behavior:** Execute JavaScript
   - **Content Source:** OnClick JavaScript
4. Paste the code below into the code editor.
5. Click **Save**.

## Step 2: Write the JavaScript

Here's the complete script:

```javascript
{!REQUIRESCRIPT("/soap/ajax/60.0/connection.js")}

var record = new sforce.SObject("Opportunity");
record.Id = "{!Opportunity.Id}";
record.StageName = "Closed Won";

var result = sforce.connection.update([record]);

if (result[0].success === "true") {
    window.location.reload();
} else {
    alert("Update failed: " + result[0].errors.message);
}
```

Let's look at what each part does.

**`{!REQUIRESCRIPT(...)}`** loads the Salesforce AJAX Toolkit, which gives you the `sforce` object. Use the API version your org supports. Version 60.0 is an example, so match it to a version available in your org.

**`new sforce.SObject("Opportunity")`** creates a record object to send to the server.

**`record.Id = "{!Opportunity.Id}"`** uses a merge field to insert the ID of the record currently on screen. Merge fields like this are resolved before the script runs, so the value is filled in for you.

**`sforce.connection.update([record])`** sends the change to Salesforce. It takes an array, so you can update several records at once by adding more objects to it.

**The `if` block** checks the result. On success, the page reloads so the user sees the new value. On failure, the user gets an alert with the error message.

## Step 3: Add the Button to the Page Layout

A button does nothing until it's on a layout.

1. Go to **Object Manager**, select the object, and click **Page Layouts**.
2. Open the layout your users see.
3. In the palette, find **Buttons** and drag **Mark as Closed Won** into the Detail Page Button section.
4. Click **Save**.

## Step 4: Test It

Test with a user who has the same profile and permissions as your end users. Administrators can see and edit more than most users, so an admin test can hide problems.

Check these scenarios:

- A record where the update should succeed.
- A record that's already in the target stage. Make sure it doesn't cause confusing behavior.
- A user without edit access to the field. They should see the error alert, not a silent failure.

## Things to Watch For

**Validation rules.** If a validation rule blocks the change, the update fails and the error message appears in the alert. Make sure your error message makes sense to users.

**Required fields.** If the record is missing a required field, the update fails. Consider checking this in your script or documenting it for users.

**Workflow and triggers.** Updates from a button run your triggers and automation like any other update. A change that looks small can fire other logic.

**Hardcoded values.** The stage name `"Closed Won"` is fixed. If your org uses a different picklist value, change it to match. Mismatched values will cause the update to fail.

**Governor limits.** Each button click uses one API call. This is fine for individual records, but bulk operations need a different approach, such as a list view button or a batch Apex job.

## Wrapping Up

A button that updates a field in one click saves users time and reduces data entry errors. The pattern is simple: add a Detail Page Button with Execute JavaScript, use `sforce.connection.update` to change the field, and place the button on the page layout.

Once you have the basic version working, you can extend it. Add a confirmation prompt with `confirm()`, pass in different values for different buttons, or update related records in the same call.

Have you built buttons like this in Classic? Share your approach in the comments.
