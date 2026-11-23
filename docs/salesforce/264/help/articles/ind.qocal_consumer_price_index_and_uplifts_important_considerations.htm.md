---
article_id: ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm
title: CPI and Renewal Price Uplift Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_renewal_price_uplifts.htm
fetched_at: 2026-11-23
---

# CPI and Renewal Price Uplift Considerations

Familiarize yourself with the supported product types, field behaviors, and system logic for applying Consumer Price Index (CPI) and renewal price uplifts. Understanding these constraints ensures accurate pricing calculations during asset renewal and helps you determine where uplift data appears in the price waterfall.

Product and Field Support

Review these functional limitations for price uplifts to ensure your products and quote lines support the feature.

CPI renewal price uplifts apply only to termed assets.
One-time and evergreen assets don’t support price uplifts.
Usage-based products don’t support price uplifts.
Derived pricing products don't support price uplifts.
Ramped quote line items and order line items don’t support the Price Uplift field.
System Behavior and Pricing Logic

Understand how the system processes uplift data during the renewal phase.

Renewal uplift percent appears in the price waterfall.
If the asset pricing source is list price, the system ignores the uplift field and doesn’t uplift the price at renewal time.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
