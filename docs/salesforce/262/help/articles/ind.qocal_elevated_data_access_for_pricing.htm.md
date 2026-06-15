---
article_id: ind.qocal_elevated_data_access_for_pricing.htm
title: Secure Data Access for Pricing with Elevated Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_elevated_data_access_for_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Secure Data Access for Pricing with Elevated Permissions

Protect sensitive data from unauthorized access and have business continuity during sales transaction pricing. This feature helps sales users to price quotes and orders without needing field-level security (FLS) to query, view, or modify the underlying sensitive fields.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To configure data access in quotes and orders:	

Salesforce admin

OR

Customize Application

AND

Manage Profiles and Permission Sets permission


To create and deploy the Pricing Procedure Apex hook class:	Author Apex permission

Before you begin:

In Setup, find and select Revenue Settings. In the Pricing section, turn on Elevated Data Access for Quotes and Orders and Procedure Plan Orchestration for Pricing.
Turn on both settings to apply elevated access to the full pricing execution path, including Procedure Plan Orchestration.

By default, Revenue Cloud's context and pricing services run under the profile of the logged-in user. Elevated Data Access for Quotes and Orders helps the Revenue Cloud pricing engine internally access sensitive fields to calculate prices, even when a user's profile lacks field-level security on those fields.

Users without FLS can price new-sale and amendment, renewal, and cancellation quotes and orders end-to-end. They’re restricted from querying, viewing, or modifying the underlying protected data. Your Salesforce admin controls which sensitive fields the pricing engine uses by creating a custom Apex hook that determines the field inputs to use in the pricing context.

This feature helps you apply strict field-level security to sensitive financial data while allowing sales reps to complete pricing tasks end-to-end.

Configure field-level security on sensitive fields. See Set Field-Level Security for a Field on All Profiles and Assign Permission Set Groups to Users.
Identify all fields that feed into your pricing procedure. For example, cost-book lookup fields, cost-plus inputs, or discount table fields. Work with your pricing procedure author to get a complete list.
Remove Read and Edit access for those fields on any profile that shouldn’t view the sensitive pricing data.
Review the page layouts, list views, or reports accessible to the restricted profile to verify that those fields aren’t available. Removing the FLS is the authoritative control. Hiding fields from layouts alone isn’t sufficient.
Confirm that the fields remain available to the system or pricing admin profile used to run the elevated pricing context.
Create the pricing procedure Apex hook. See Customize Your Procedure Plans with Apex Hooks.
Implement the appropriate pricing hook interface (pre-pricing or post-pricing or both).
In the pre-pricing hook, add or validate the sensitive fields that the engine needs internally.
In the post-pricing hook, strip those fields from the context output before it’s returned to the calling user context.
Deploy and register the Apex class in your Pricing Procedure configuration.
Verify your setup.
Log in as a user with the restricted profile (a sales rep without FLS on the sensitive fields).
Open a quote or order and trigger pricing.
Confirm that the price calculates successfully and the correct output values appear on the transaction.
Confirm that the sales rep can’t see the restricted fields in the record detail, in list views, or through reports.
As a Salesforce admin, run a test to confirm that the Apex hook fires, for both pre-pricing and post-pricing stages, without errors.
