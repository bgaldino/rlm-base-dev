---
article_id: ind.dro_assetization_rules_for_dynamic_revenue_orchestrator.htm
title: Assetization Rules for Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_assetization_rules_for_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Assetization Rules for Dynamic Revenue Orchestrator

Use Asset Lifecycle Management to create and activate multiple asset-based orders (ABOs) for the same asset across different sales transactions or orders. Maintaining precise assetization rules makes sure that the system applies changes sequentially and prevents data conflicts during the fulfillment process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Fulfillment Integrity and Asset Changes

Run an invocable action or Apex and add it to the order submit flow to apply exactly one change to an asset at a time. This sequential processing avoids failures during the fulfillment process. When an order item or order action applies to an asset after the invocable action runs, the system prevents the assetization of previously created order items for that asset due to outdated data.

Asset Verification Details

Load the quote line items or order line items to determine the creation date for each asset related to an order line item. Verify these specific details for each quote line item or order line item.

Determine if the created date of the quote line item or order item matches the created date of the most recent asset action.
Determine if the created date of the asset action is more recent than the created date of the quote line item or order item.
