---
article_id: ind.qocal_add_custom_fields_for_usage_based_products.htm
title: Create and Add Custom Fields for Usage-Based Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_add_custom_fields_for_usage_based_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Create and Add Custom Fields for Usage-Based Products

Ensure that your custom fields are visible to users during sales transactions. By default, custom fields aren’t visible on the quote creation, manage usage resource, and asset pages.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

To show custom fields on the Manage Usage Resources page while creating quotes or orders, create custom fields on these objects:

Quote Line Rate Card Entry
Quote Line Rate Adjustment
Order Item Rate Card Entry
Order Item Rate Adjustment

To show custom fields on the usage-related tabs on an asset page, create the custom fields on these objects:

Asset Rate Card Entry
Asset Rate Adjustment

After creating the fields, map them in the context definitions to support them in your sales transactions.

NOTE Usage products support custom fields with the Text, Text Area, Number, Checkbox, Date, Percent, Currency, and Picklist data types.
Create custom fields: Use Object Manager to add fields to relevant sales objects (for example, Quote, Order, Product).
Add attributes: Add corresponding attributes and tag names to the extended context definition.
Map attributes: Map these attributes to the custom fields on the entity.
Update the context definition of the rating discovery procedure.
From the App Launcher, find and select Rating Discovery Procedures.
Open the rating discovery procedure used to get rates, and deactivate it.
Go to the rating discovery procedure page, and click Edit.
In Context Definition, select the new extended context definition with custom fields.
Save your changes.
Open the rating discovery procedure, and activate it.
Add custom fields to the page layout.
Go to a record page, click the settings icon, and then click Edit Page.
For adding custom fields to the Manage Usage Resources page, edit a quote or an order record page. And for adding fields to assets, edit an asset record page.
Select the Usage Rates component.
Custom fields aren't supported for the Usage Rates component on the Account, Contract, and Binding Object Custom Extension record pages.
In the right panel, click Select for Select custom fields for the Usage Rates card.
Move the custom fields from the Available list to the Selected list, and then click OK.
Save the changes.
On Activation: Asset Record Page, select APP DEFAULT, and then click Assign as App Default.
In Select Apps, select Usage Management.
Click Next, and save your changes.

The custom fields are now visible for the Manage Usage Resources page, and under the Rates tab for an Asset record page.
