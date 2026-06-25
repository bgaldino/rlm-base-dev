---
article_id: ind.collections_create_custom_fields_account.htm
title: Create Custom Account Fields for Collections Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_custom_fields_account.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_insights_account_page.htm
fetched_at: 2026-06-21
---

# Create Custom Account Fields for Collections Summary

Add custom fields to the Account object to store aggregated collections data, such as total initial due amount, total current total due amount, total payments received, and average days past due. Set field-level security to these fields.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create custom fields on the Account object:	

Collections and Recovery Admin permission set

And

Customize Application permission


To set field-level security for custom fields:	

Collections and Recovery Admin permission set

And

Manage Profiles and Permission Sets permission

And

Customize Application permission

Make sure that you create these custom fields with the specified API names and data types. If you plan to use different API names, make sure to update the custom field references in the predefined Data Processing Engine definition.

CUSTOM FIELD API NAME	DATA TYPE
AccountTotalCurrentDueAmount	Currency (Length: 16, Decimal Places: 2)
AccountTotalInitialDueAmount	Currency (Length: 16, Decimal Places: 2)
AccountTotalPaymentsReceived	Currency (Length: 16, Decimal Places: 2)
AccountAverageDaysPastDue	Number (Length: 9, Decimal Places: 0)

The custom fields that you create are referenced in the predefined Data Processing Engine definition's writeback object configuration.

To store the key collections metrics, create the custom fields on the Account object.
Set the field-level security for the newly created custom fields on the Account object.
