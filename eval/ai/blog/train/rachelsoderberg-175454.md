# Update Salesforce Fields With A Button Click (Salesforce Classic)

Salesforce Classic provides various ways to interact with your data, but sometimes you need to quickly update records without navigating through the standard editing interface. One powerful way to accomplish this is by using custom buttons that perform field updates. This guide walks you through creating a button that updates Salesforce fields with a single click.

## Understanding Custom Buttons in Salesforce Classic

Custom buttons in Salesforce Classic allow you to execute actions that go beyond the standard interface. You can create buttons that update fields, run JavaScript, call external services, or execute flows and processes. For our purposes, we'll focus on using buttons to update field values.

The beauty of custom buttons is that they appear directly on record pages and list views, making common operations just one click away for your users.

## Prerequisites

To create custom buttons in Salesforce Classic, you'll need:

- Administrator access to your Salesforce org
- The appropriate object where you want to add the button
- Understanding of the fields you want to update

## Method 1: Using a Button to Open an Update Dialog

The simplest approach is to create a button that opens a dialog allowing users to update specific fields. We'll use Salesforce's built-in update page.

1. Navigate to Setup and go to the object where you want to add the button (e.g., Accounts)
2. Click "Buttons, Links, and Actions"
3. Click "New Button or Link"
4. Configure the button:
   - Label: "Update Status"
   - Name: "Update_Status"
   - Display Type: "Detail Page Button" or "List View Button"
   - Behavior: "Open a URL"
   - Content Source: "URL"

5. In the URL field, enter:
```
/{your_object_id}/e?retURL=/{your_record_id}
```

This method has limitations—it requires users to manually select and update fields in the edit dialog.

## Method 2: Using JavaScript to Update Fields Directly

For a more powerful solution, use JavaScript to update fields directly. This is more advanced but gives you much more control.

Create a button with these settings:
- Display Type: "Detail Page Button"
- Behavior: "Execute JavaScript"
- Content Source: "OnClick JavaScript"

In the JavaScript editor, enter:

```javascript
var recordId = '{!Account.Id}';
var accountName = '{!Account.Name}';

// Create an update request
var url = '/{accountId}/e?retry=1';
if(document.referrer.indexOf('list') >= 0) {
  url = url + '&retURL=' + document.referrer;
} else {
  url = url + '&retURL=/' + recordId;
}

window.location = url;
```

## Method 3: Using Visual Workflow (Recommended)

The most flexible modern approach is to combine a custom button with a Visual Workflow. Workflows can handle complex logic and multiple field updates.

1. Create a Flow:
   - Go to Setup > Create > Workflows & Approvals > Flows
   - Click "New Flow"
   - Create a flow that updates your desired fields
   - Add any logic you need (conditionals, loops, etc.)

2. Create a Button that invokes the flow:
   - Display Type: "Detail Page Button"
   - Behavior: "Open a URL"
   - Content Source: "URL"
   - URL:
```
/flow/YourFlowName?retURL=/{!Account.Id}
```

## Practical Example: Status Update Button

Let's create a practical example. Suppose you want to add a "Mark as Active" button that updates an Account status to "Active" and sets the Last Modified Date.

1. Navigate to Setup > Customize > Accounts > Buttons, Links, and Actions
2. Click "New Button or Link"
3. Fill in:
   - Label: "Mark as Active"
   - Name: "Mark_as_Active"
   - Display Type: "Detail Page Button"
   - Behavior: "Execute JavaScript"

4. In the JavaScript content, enter:

```javascript
var id = '{!Account.Id}';
var newUrl = '/{id}/e?AccountStatus=Active&retURL=/{id}';
newUrl = newUrl.replace(/{id}/g, id);
window.location = newUrl;
```

## Adding the Button to Your Layout

After creating your button, you need to add it to your page layout so users can see it:

1. Go to Setup > Customize > Accounts > Page Layouts
2. Edit the page layout where you want the button to appear
3. Drag your button from the palette to the layout
4. Save the page layout

The button will now appear on Account record pages.

## Advanced Option: Using AJAX

For more sophisticated implementations, you can use AJAX to update records without reloading the page:

```javascript
var id = '{!Account.Id}';
var xmlhttp;

if (window.XMLHttpRequest) {
  xmlhttp = new XMLHttpRequest();
} else {
  xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
}

var url = "/services/data/v54.0/sobjects/Account/" + id;
var updatedData = {
  "Status__c": "Active",
  "Last_Updated__c": new Date().toISOString()
};

xmlhttp.open("PATCH", url, true);
xmlhttp.setRequestHeader("Authorization", "Bearer {!$API.Session_ID}");
xmlhttp.setRequestHeader("Content-Type", "application/json");
xmlhttp.onreadystatechange = function() {
  if (xmlhttp.readyState == 4 && xmlhttp.status == 204) {
    alert('Record updated successfully');
    location.reload();
  }
};
xmlhttp.send(JSON.stringify(updatedData));
```

## Best Practices

Keep button operations simple. If the update logic becomes complex, consider using a Flow instead.

Always test your buttons thoroughly. Make sure they work with various user profiles and permissions.

Consider user experience. If multiple field updates are needed, group them logically.

## Conclusion

Custom buttons in Salesforce Classic provide a powerful way to streamline common operations. Whether you use simple redirects to an edit page, JavaScript to update multiple fields, or Visual Workflows for complex logic, custom buttons can significantly improve your users' productivity. Choose the method that best fits your use case, and your users will appreciate the saved clicks.