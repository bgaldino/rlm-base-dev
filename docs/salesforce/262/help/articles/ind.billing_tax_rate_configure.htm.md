---
article_id: ind.billing_tax_rate_configure.htm
title: Configure Tax Rates
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_rate_configure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Tax Rates

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Configure Tax Rates

Use the Revenue Standard Tax Engine to calculate taxes natively in Agentforce Revenue Management. Define tax rates and use the built-in decision table to determine applicable taxes for products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To configure tax rates:	

Tax Admin permission set

To streamline tax rate configuration, make sure to provide sharing access and sharing rules for the Geo Country and Tax Rate objects.

From the App Launcher, find and select Tax Rates.
Click New.
Verify that the rate application is set to Agentforce Revenue Management.
Enter a tax code.
The tax code defined here is used in tax treatment and tax treatment item records to determine how the tax rate is applied. Ensure that the same tax code is consistently referenced across tax configurations so the correct rate is applied during transaction processing.
Enter the geo country or geo state where the rate applies.
Geo Country and Geo State records must be created with the correct ISO code.
Select a currency ISO code.
This field is available for multi-currency orgs only. If you’re unable to view this field, add it from the page layout.
Enter the tax rate as a percentage or flat amount.
Agentforce Revenue Management doesn't validate tax percentage or flat tax amount values. Make sure that the tax percentage is greater than 0% or the flat tax amount is a positive value.
Select the application basis.
See Understand How Agentforce Revenue Management Determines and Applies Tax Rates section to know how the gross and net taxes are used in tax calculation.
Enter a priority.
When multiple tax rates match a transaction, Agentforce Revenue Management uses this value to determine the execution order. Lower values run first, with priority 1 taking precedence over priority 2 and so on.
Enter the product code if the tax rate is specific to a product.
You can find the product code from the respective products in your Salesforce org. For example, the invoice line includes a reference to the associated product. The product code specified here is matched against the product code on the transaction to determine the applicable tax rate.
Enter the start date and end date to define the validity of this tax rate record.
Select a legal entity.
Agentforce Revenue Management doesn’t mandate a legal entity entry, but you must add one to manage and map tax rates to transactions by legal entity.
Save your changes.
Check for and refresh the Revenue Standard Tax Entries decision table every time a tax rate record is modified or added in your Salesforce org. See Also.

Create a Tax Engine record with the type set to Revenue Standard Tax Engine. Next, create the Tax Policy and Tax Treatment records, making sure the Tax Treatment references the tax engine record with type set to Revenue Standard Tax Engine. Finally, assign the appropriate tax policy to the relevant products.

To maintain consistency and data integrity with country and state values that are used in addresses, it’s recommended to enable State and Country picklists. See Enable State and Country/Territory Picklists, Create Geo Countries for the Manual Salesforce Tax Solution, and Create Geo States for the Manual Salesforce Tax Solution.
