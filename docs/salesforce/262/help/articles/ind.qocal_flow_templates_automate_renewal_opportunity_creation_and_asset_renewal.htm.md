---
article_id: ind.qocal_flow_templates_automate_renewal_opportunity_creation_and_asset_renewal.htm
title: Asset Renewal Automation Templates
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_flow_templates_automate_renewal_opportunity_creation_and_asset_renewal.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Asset Renewal Automation Templates

Prebuilt flow templates automatically create renewal opportunities for forecasting and renewing assets. Customize these templates to meet specific business needs before activation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

For example, update Text Template resources to capture more information or match your company's voice, and enter values in the Configure Sender Details section to specify the outgoing email address.

Flow Template Details

Review the descriptions and prerequisites for each flow before activation.

FLOW NAME	DESCRIPTION	PREREQUISITES
Create and Update Renewal Opportunities	

This flow creates opportunity records for renewable assets during order assetization.

If multiple assets share an end date, the flow adds them to the same opportunity record.

	
If your Salesforce org uses multiple currencies, customize the flow to assign asset CurrencyIsoCode values to opportunity products.
Customize the flow to assign the median of net unit prices of a product as the opportunity product net unit price.
Edit the OpportunityName constant to change the name of created opportunity records.
When associating a contract with the order, specify the Renewal Term and Renewal Term Unit on the contract before activating the order.

Automatically Renew Expiring Assets	This flow creates and activates renewal orders for assets set to expire and marked for automatic renewal.	
Assign the InitiateRenewal API permission set to the default workflow user.
Edit page layouts to show the auto-renewal fields.
Show the Automatically Renew Asset by Default field on Product Selling Model pages.
Show the Automatically Renew field on Quote Line Item, Order Item, and Asset pages. See Customize the Transaction Line Editor and Add the Managed Asset Viewer to the Account and Contract Page Layouts.
Product designers and sales reps use these fields to selet products for automatic renewal.
Edit the NumberOfDaysInTheFuture variable to change how many days before expiration the asset renews.
Edit the RetryCount variable to change how many times the flow tries order activation again.
Set a condition to prevent the renewal of discontinued products.
