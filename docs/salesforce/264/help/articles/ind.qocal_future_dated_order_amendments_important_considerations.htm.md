---
article_id: ind.qocal_future_dated_order_amendments_important_considerations.htm
title: Considerations for Assets with Future-Dated Changes
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_future_dated_order_amendments_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-11-23
---

# Considerations for Assets with Future-Dated Changes

Keep these considerations in mind when amending, renewing, canceling, transferring, or swapping assets with future-dated changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
You can renew an asset with a future-dated renewal already scheduled.
You can’t amend, renew, or cancel before a future asset state period on ramp deals.
You can’t use derived-pricing products (DPP) for future-dated ARC transactions. If the amended date results in a future-dated change, you can’t add DPP assets to a future-dated transaction or select a DPP asset.
You can’t amend a usage-based product with a future-dated and back-dated change.
You can’t reduce the quantity (over-reduce) beyond the quantity between the quote line item’s start and end dates.
You can’t use a rollback amendment to roll back a future-dated amendment change.
You can amend a future-dated order with products that have Constraint Modeling Language rules set up. However, the amendment doesn’t conform to all the rules.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_future_dated_order_amendments_important_considerations.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
