---
article_id: ind.qocal_renewal_rate_and_grant_sourcing_consideratins.htm
title: Renewal Rate and Grant Sourcing Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renewal_rate_and_grant_sourcing_consideratins.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-11-23
---

# Renewal Rate and Grant Sourcing Considerations

Review these behaviors before renewing usage-based assets.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Advanced license.
Asset-level configuration: Set Pricing Source separately on each asset. There isn't an org-wide default for retaining negotiated rates and grants.
Last-transaction values: When Pricing Source is Last Transaction, renewal quotes use the negotiated rates and original sold grant quantities recorded for the asset.
Catalog values: When Pricing Source is blank or uses catalog pricing, renewal quotes use active catalog rates and grants.
Per-resource fallback: If an asset doesn't contain a rate or grant for a usage resource, the renewal quote uses the active catalog value for only that resource.
Commitment products: Selected usage resources retain their negotiated values. Optional resources added during renewal use active catalog values.
Ramp products: Each segment uses the asset values that are effective for its dates. Segments beyond the asset's final segment use the last active rates and grants.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_renewal_rate_and_grant_sourcing_consideratins.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
