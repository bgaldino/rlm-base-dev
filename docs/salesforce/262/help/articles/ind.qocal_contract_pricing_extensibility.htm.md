---
article_id: ind.qocal_contract_pricing_extensibility.htm
title: Set Up Contract Pricing Extensibility
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_contract_pricing_extensibility.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Contract Pricing Extensibility

Define unique Contract Item Price (CIP) records by using custom fields to bypass default uniqueness checks and record validations. This extensibility helps your business to set flexible contract pricing based on custom parameters that match your specific organizational needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To set up contract pricing extensibility:	Salesforce admin

By default, Agentforce Revenue Management provides one negotiated contract price per unique product and Product Selling Model (PSM) combination for a specific date range. This restriction prevents you from defining multiple Contract Item Price (CIP) records for the same product and PSM during overlapping effective dates.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on Advanced Order Creation From Quote to generate multiple orders from a single quote.
Turn on Customize Contract Pricing to define unique contract item prices based on custom fields.
To apply contract item prices with custom fields at run time, complete these additional setup steps.
Add a custom field, such as Location__c, to the Contract Item Price (CIP), Order Item, and Quote Line Item (QLI) objects.
Add the custom field to the Contract Pricing Entries decision table.
Update your default pricing procedure to include the new custom field.
Update context definition mappings for QuoteEntitiesMapping and OrderEntitiesMapping to map STI.ItemCustomFieldId to both QuoteLineItem.CustomFieldId and OrderLineItem.CustomFieldId.
Save your changes.
