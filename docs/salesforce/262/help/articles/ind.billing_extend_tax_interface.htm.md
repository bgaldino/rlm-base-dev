---
article_id: ind.billing_extend_tax_interface.htm
title: Extend Your Tax Interface
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_extend_tax_interface.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Extend Your Tax Interface

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Extend Your Tax Interface

Enhance the existing tax interface by mapping additional fields for tax callouts. Use custom metadata types to send additional data in tax requests and persist more detailed information from tax responses.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Tax Interface Extension
Handle tax calculation needs that go beyond standard integrations, capture the right data for audits, and adapt to new requirements through configuration instead of custom code.
Configure Your Custom Metadata Types
Create a custom metadata type to house your field mappings. These field mappings are required for all the additional fields you want to include in your tax callouts. Associate your custom metadata type with your tax engine provider so it's aware of the fields used in the request and response.
