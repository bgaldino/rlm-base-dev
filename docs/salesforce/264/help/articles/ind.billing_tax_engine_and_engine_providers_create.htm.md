---
article_id: ind.billing_tax_engine_and_engine_providers_create.htm
title: Create a Tax Engine Provider and Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_engine_and_engine_providers_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_partner_or_custom_tax_engine.htm
fetched_at: 2026-09-04
---

# Create a Tax Engine Provider and Tax Engine

If you use a partner app or your own engine, create a tax engine provider and a tax engine.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create tax engine providers and tax engines:	Tax Admin permission set

Make sure that you complete the prerequisites before you create a tax engine provider and tax engine.

Create a Tax Engine Provider

Create a tax engine provider to store information about the Apex adapter class that manages communication with the tax engine.

From the App Launcher, find and select Tax Engine Providers.
Click New.
Enter a label and API name for the tax engine provider.
Select the ID of the Apex adapter that you want the tax engine provider to use.

If you use your own tax engine, select the custom tax adapter that you configured.

NOTE Select a unique Apex adapter for each tax engine provider.
If you have extended tax callouts, enter the API name of the custom metadata type you created.
Save your changes.
Create a Tax Engine

Create a tax engine record that Billing uses to calculate tax. Include the tax engine provider, named credential, seller code, and address.

From the App Launcher, find and select Tax Engines.
Click New.
Enter a name for the tax engine.
Select the type as Revenue Cloud Tax Extension.
Select the tax engine provider.
Select the named credential that you created to authenticate the tax engine.
Enter the seller code of the tax provider.
Enter the address of the tax provider.
Select the status as Active.
You can use only active tax engines to calculate taxes.
To capture taxes at the header level, select Capture Taxes At Header.
The Capture Taxes At Header checkbox appears only when Credit, Payment, and Refund Application Level is Header Level. See Capture Taxes at Header Level.
Save your changes.

Create tax policies and treatments. If the tax treatment is taxable, select this tax engine on the tax treatment. Then assign the tax policy to the relevant products. When Billing calculates tax for an order product, it uses the tax engine on the product’s tax treatment.

NOTE Make sure that your tax engine supports tax calculation for credits used for negative invoice lines and credit memos. If the tax engine doesn’t support credits, Billing can’t process negative invoice lines and invoice void operations fail.
