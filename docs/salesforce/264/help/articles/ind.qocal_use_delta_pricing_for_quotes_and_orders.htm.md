---
article_id: ind.qocal_use_delta_pricing_for_quotes_and_orders.htm
title: Set Up Delta Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_use_delta_pricing_for_quotes_and_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_features_in_revenue_cloud.htm
fetched_at: 2026-09-04
---

# Set Up Delta Pricing

Improve large transaction performance by enabling Delta Pricing to recalculate only modified quote or order lines and their dependencies.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

Delta Pricing optimizes performance by recalculating only modified quote or order lines and their dependent lines rather than the entire transaction. This background process requires no at run time user interface changes. The system applies Delta Pricing automatically to transaction updates that lack validation errors and follow a successful previous pricing run. If the transaction fails to meet these criteria, the system performs a full repricing.

IMPORTANT Turn off Dual Persistence mode before you use Delta Pricing, as these features are incompatible.
From Setup, in the Quick Find box, search for and select Revenue Settings.
Turn on Delta Pricing for Quotes and Orders.
