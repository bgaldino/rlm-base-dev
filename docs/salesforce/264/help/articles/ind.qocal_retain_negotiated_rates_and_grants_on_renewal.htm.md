---
article_id: ind.qocal_retain_negotiated_rates_and_grants_on_renewal.htm
title: Retain Negotiated Rates and Grants on Renewal
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_retain_negotiated_rates_and_grants_on_renewal.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amending_rates_and_grants_on_usage_based_products.htm
fetched_at: 2026-11-23
---

# Retain Negotiated Rates and Grants on Renewal

To keep a customer's negotiated usage terms on a renewal quote, set the asset's Pricing Source to Last Transaction before renewal. This configuration applies separately to each asset. If Pricing Source is blank or uses catalog pricing, the renewal quote uses active catalog rates and grants.

NOTE Setting Pricing Source to Last Transaction also carries over the product's price from the last transaction, not just the usage terms.

The renewal quote uses the terms recorded for the asset's last activated transaction. Grant sourcing uses the original sold grant quantity for the new term, not the customer's remaining or unconsumed grant balance. If a usage resource doesn't have an asset-level rate or grant, the renewal quote uses the active catalog value for that resource.

Rate and grant retention applies to auto, on-time, early, and late renewals for supported usage-based products.

Anchor, pack, and commitment products
The renewal quote carries forward the asset's negotiated rates and grants. Pack resources rebind to the renewed anchor product.
Commitment products
The renewal quote carries forward selected usage resources and their negotiated values. Optional resources added during renewal use active catalog values.
Ramp products
Each renewal segment uses the asset values that are effective for the segment's dates. A segment that extends beyond the asset's final segment uses the last active rates and grants.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_retain_negotiated_rates_and_grants_on_renewal.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
