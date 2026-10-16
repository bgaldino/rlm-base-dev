---
article_id: ind.billing_partner_or_custom_tax_engine.htm
title: Partner or Custom Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_partner_or_custom_tax_engine.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_tax_configuration.htm
fetched_at: 2026-09-04
---

# Partner or Custom Tax Engine

When you need complex tax jurisdictions or already use a tax vendor, you connect a partner tax app or your own tax engine. The TaxEngineAdapter Apex interface retrieves information from the tax engine and evaluates the information to define tax details.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Prerequisites for a Partner or Custom Tax Engine
If you want to calculate taxes by using your own tax engine or by integrating the Billing TaxEngineAdapter Apex interface with a partner app, complete these prerequisites.
Configure Additional Tax Identification Details
Send additional tax identification details to your external tax engine. Meet regional tax compliance requirements by storing tax identification and exemption information on the Billing Account and passing it to the tax engine.
Extend the Revenue Cloud Tax Extension Engine
Enhance the existing tax interface by mapping additional fields for tax callouts. Use custom metadata types to send additional data in tax requests and persist more detailed information from tax responses.
Create a Tax Engine Provider and Tax Engine
If you use a partner app or your own engine, create a tax engine provider and a tax engine.
