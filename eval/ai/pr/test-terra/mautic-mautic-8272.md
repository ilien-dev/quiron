## Description

This PR updates Mautic’s Zoho CRM integration to use Zoho’s REST v2 API. The integration previously relied on an older version of the API; this change brings it in line with Zoho’s v2 interface so that Mautic can continue communicating with Zoho CRM.

The update affects the connection between the two systems and the requests used by the integration. Review should focus on whether an administrator can configure the integration and whether contact data continues to move as expected using the configured field mappings.

## Why this change is needed

Teams use the Zoho integration to share contact information between Mautic and their CRM. An API version change can affect both the initial connection and subsequent synchronization, so updating the integration is necessary to maintain that workflow.

This PR moves the integration to Zoho’s v2 API. It should be evaluated against both a new configuration and an existing integration, since the upgrade needs to work for administrators setting up Zoho for the first time as well as those already using it.

## How to test

A Zoho CRM account and a Mautic test instance are needed for the integration checks. Use test records that can be identified easily in both systems.

1. Apply this PR to a test instance and clear the Mautic cache.
2. Open the Zoho integration settings. Configure the connection and complete any authorization steps required by the integration.
3. Confirm that the connection can be saved and that Zoho fields are available for mapping. Map a small set of fields, including an email address and a name.
4. Create a test contact in Mautic and run the configured synchronization. Check Zoho CRM for the corresponding record and confirm that the mapped values match.
5. Change a mapped value on the test record and run synchronization again. Confirm that the expected record is updated and that an unexpected duplicate is not created.
6. If your configuration supports synchronization from Zoho to Mautic, make a change in Zoho and confirm that it appears in Mautic after the relevant sync runs.
7. Reopen the integration settings and confirm that the connection and field mappings remain available. Check the Mautic logs for errors during authorization and synchronization.

For an upgrade test, repeat the relevant steps with an existing Zoho integration and its field mappings. Pay particular attention to whether the connection needs to be authorized again and whether the expected records are matched after the update.

## Expected result

The Zoho integration connects through the REST v2 API, exposes the fields needed for mapping, and synchronizes the test data according to the integration’s configuration. An existing integration should be checked for any configuration or authorization changes needed after the upgrade.

These are proposed manual checks; their results should be recorded during review. Mautic’s [2.16 release announcement](https://mautic.org/?p=16635) identifies this PR as the Zoho CRM v2 API update.
