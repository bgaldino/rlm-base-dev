---
article_id: ind.billing_tax_configuration_prerequisites.htm
title: Prerequisites for a Partner or Custom Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_configuration_prerequisites.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_partner_or_custom_tax_engine.htm
fetched_at: 2026-09-04
---

# Prerequisites for a Partner or Custom Tax Engine

If you want to calculate taxes by using your own tax engine or by integrating the Billing TaxEngineAdapter Apex interface with a partner app, complete these prerequisites.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Gather Tax Provider Details

If you want to use a tax service provider, gather this information:

Tax provider’s seller code
Tax provider’s mailing address
Credentials for accessing the tax provider
Create a Named Credential

After you gather the tax provider details, create a named credential to secure and authenticate API callouts to the tax engine.

Define a Custom Apex Adapter

If you use your own tax engine, define a custom tax adapter by extending the TaxEngineAdapter Apex interface.

You can model your custom tax adapter’s implementation based on this example.

From Summer ’25, Billing supports up to 2000 invoice lines for a single invoice. To avoid limit-related issues, test your TaxEngineAdapter Apex interface’s implementation to make sure that it adheres to the Apex limit for total heap size.
