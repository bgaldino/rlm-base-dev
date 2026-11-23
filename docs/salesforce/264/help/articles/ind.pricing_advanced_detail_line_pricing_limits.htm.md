---
article_id: ind.pricing_advanced_detail_line_pricing_limits.htm
title: Advanced Detail Line Pricing Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_advanced_detail_line_pricing_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm
fetched_at: 2026-11-23
---

# Advanced Detail Line Pricing Limits

Before you add the Advanced Detail Line Pricing element to a pricing procedure, review these limitations and configuration requirements.

When Advanced Detail Line Pricing is enabled, the Map Line Item element can't update fields at the header level. To update a header-level field, disable Advanced Detail Line Pricing.
Avoid using the Advanced Detail Pricing and Map Line Item elements in the same procedure because they perform the same operation.
When Advanced Detail Pricing is enabled, Derived Pricing element produces inaccurate results for quote line item details.
Advanced Detail Line Pricing doesn't support parallel execution. To use this feature, turn off parallel execution for the pricing procedure.
The pricing procedure doesn't validate Advanced Detail Line Pricing configuration at design time.
The Stop Pricing element doesn't work when Advanced Detail Line Pricing is turned on.
The Aggregate Price element doesn't work for group calculations when Advanced Detail Line Pricing is turned on.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_advanced_detail_line_pricing_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
