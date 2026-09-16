---
article_id: ind.qocal_product_variation_important_considerations.htm
title: Considerations for Adding Product Variations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_product_variation_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_product_variation_use_in_transaction_management.htm
fetched_at: 2026-09-04
---

# Considerations for Adding Product Variations

Keep these considerations in mind for product variations when managing and selling assets.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Variation parent and child products don’t support dynamic attributes, but you can have a combination of variation products and configurable product line items in a sales transaction.
You can include product variations as part of static bundles, but not configurable bundles.
The Change action isn’t available on amendment, renewal, or cancellation orders.
The Change action isn’t available on bundle components.
The Change action isn’t available for ramped groups.
The Change action isn’t available on supplemental order items.
You can’t swap an asset for a variation product by using the UI. The alternative is to use the swap API.
