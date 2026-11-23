---
article_id: ind.billing_setup.htm
title: Set Up Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-11-23
---

# Set Up Billing

Enable Billing, assign the required permission sets, and set up features.

Select Default Billing Treatment, Tax Treatment, and Legal Entity
If there's no billing policy specified for order products, the default billing treatment defines how those order products are billed. The default tax treatment is used with all order products unless overriden on specific order products or tax policies. The default legal entity is used with quotes and orders to calculate taxes unless overriden for specific quotes and orders.
Configure Context Definitions for Billing
Context definitions in Billing act as a central data-mapping layer that helps information flow seamlessly from orders or external transactions into billing schedules. They transform data from Salesforce objects into a standardized format that enable the Billing APIs to read the details required to create accurate billing records. By configuring these context definitions, businesses can automate the transfer of custom field data.
Add New Billing Fields to Page Layouts
Provide users more context by adding new fields to the default page layouts each release.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_setup.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
