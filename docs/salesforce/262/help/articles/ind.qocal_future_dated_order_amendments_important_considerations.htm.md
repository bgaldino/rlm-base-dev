---
article_id: ind.qocal_future_dated_order_amendments_important_considerations.htm
title: Considerations for Assets with Future-Dated Changes
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_future_dated_order_amendments_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Assets with Future-Dated Changes

Keep these considerations in mind when amending, renewing, canceling, transferring, or swapping assets with future-dated changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
You can't renew an asset with a future-dated renewal already scheduled.
You can’t amend, renew, or cancel before a future asset state period on ramp deals.
You can’t use derived-pricing products (DPP) for future-dated ARC transactions. If the amended date results in a future-dated change, you can’t add DPP assets to a future-dated transaction or select a DPP asset.
You can’t amend a usage-based product with a future-date change.
You can’t reduce the quantity (over-reduce) beyond the quantity between the quote line item’s start and end dates.
You can’t back-date transactions.
You can’t use a rollback amendment to roll back a future-dated amendment change.
You can amend a future-dated order with products that have Constraint Modeling Language rules set up. However, the amendment doesn’t conform to all the rules.
