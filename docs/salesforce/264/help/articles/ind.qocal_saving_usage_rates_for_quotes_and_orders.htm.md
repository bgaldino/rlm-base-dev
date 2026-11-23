---
article_id: ind.qocal_saving_usage_rates_for_quotes_and_orders.htm
title: Saving Usage Rates for Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_saving_usage_rates_for_quotes_and_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_usage_selling_advanced_concepts.htm
fetched_at: 2026-11-23
---

# Saving Usage Rates for Quotes and Orders

Automatically save current usage rates by generating rate card entries when you save a quote or order. This process helps maintain rate consistency during the sale, even if the product catalog is updated later.

REQUIRED EDITIONS
NOTE To enable automatic rate capture, configure the Revenue Cloud transaction processing type with RatingPreference set to Fetch. The Place Sales Transaction (PST) API uses this value only when the request payload doesn't specify transaction processing preferences. If the payload specifies a preference, the PST API ignores all preferences from the default transaction processing type. For example, if the product configurator sends a value for the configurationPref in the payload, the API ignores the default RatingPreference value, and automatic rate capture doesn't occur.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
How Rate Capture Works

To support rate stability, Revenue Cloud saves usage rates at the beginning of the sales process. This prevents future catalog changes from affecting quotes in progress and helps maintain rate consistency from the quote to the order.

Revenue Cloud automatically captures catalog rates during the quoting process:

When you save a quote, Revenue Cloud captures the current catalog rates and generates a Quote Line Rate Card Entry record, which prevents subsequent catalog updates from impacting the quote.
When you successfully order the quote, Salesforce transforms those records into Order Item Rate Card Entry records to maintain the exact rates for the order.
NOTE When you add quote line items from a related list, Revenue Cloud doesn't create the quote line rate card entries immediately. The entries are created the next time the pricing service is invoked, such as when you edit a quote line item, save the quote, or assetize the quote.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_saving_usage_rates_for_quotes_and_orders.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
