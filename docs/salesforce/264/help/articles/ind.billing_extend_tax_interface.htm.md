---
article_id: ind.billing_extend_tax_interface.htm
title: Extend the Revenue Cloud Tax Extension Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_extend_tax_interface.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_partner_or_custom_tax_engine.htm
fetched_at: 2026-11-23
---

# Extend the Revenue Cloud Tax Extension Engine

Enhance the existing tax interface by mapping additional fields for tax callouts. Use custom metadata types to send additional data in tax requests and persist more detailed information from tax responses.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Tax Interface Extension
Handle tax calculation needs that go beyond standard integrations, capture the right data for audits, and adapt to new requirements through configuration instead of custom code.
Configure Your Custom Metadata Types
Create a custom metadata type to house your field mappings. These field mappings are required for all the additional fields you want to include in your tax callouts. Associate your custom metadata type with your tax engine provider so it's aware of the fields used in the request and response.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_extend_tax_interface.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
