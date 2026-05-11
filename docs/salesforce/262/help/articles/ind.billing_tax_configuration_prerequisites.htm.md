---
article_id: ind.billing_tax_configuration_prerequisites.htm
title: Tax Setup Prerequisites
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_configuration_prerequisites.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Tax Setup Prerequisites

If you want to calculate standard taxes, calculate taxes by using your own tax engine, or by integrating the Billing TaxEngineAdapter Apex interface with a partner app, complete these prerequisites.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Gather Tax Provider Details

If you want to use a tax service provider, gather this information:

Tax provider’s seller code
Tax provider’s mailing address
Credentials for accessing the tax provider
Create a Named Credential

After you gather the tax provider details, create a named credential to secure and authenticate API callouts to the tax engine.

Calculating standard taxes doesn't required a named credential. However, the Named Credentials field on the Tax Engine object is required. So, create a named credential by using an external credential that doesn't have any authentication protocol.

Define a Custom Apex Adapter

If you want to calculate standard taxes based on flat tax rates or use your own tax engine, define a custom tax adapter by extending the TaxEngineAdapter Apex interface.

To calculate standard taxes, you can model your custom tax adapter's implementation based on this example.

From Summer ’25, Billing supports up to 2000 invoice lines for a single invoice. To avoid limit-related issues, test your TaxEngineAdapter Apex interface’s implementation to make sure that it adheres to the Apex limit for total heap size.
