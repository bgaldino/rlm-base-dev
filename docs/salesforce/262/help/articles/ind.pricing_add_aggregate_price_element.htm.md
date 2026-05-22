---
article_id: ind.pricing_add_aggregate_price_element.htm
title: Calculate Aggregate Prices for Products
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_add_aggregate_price_element.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Calculate Aggregate Prices for Products

Determine the aggregate prices of a group of products by defining aggregation at multiple line item layers and ensuring pricing is calculated at the configured levels.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

Aggregate pricing summarizes prices at different levels of your sales process, providing a clear understanding of costs for bundles, quotes, or specific quote sections. The Roll-Up feature within Aggregate Price defines how prices consolidate, allowing you to specify fields like list price, discount, or net price for inclusion. By selecting Roll Up Price, you can calculate a group's total cost by first determining each child product's price and then adding that to a parent product.

IMPORTANT

Aggregate Pricing doesn't support derived products on quote line items.

To ensure accurate calculations, we recommend placing the Aggregate Price element after the Derived Price element within your procedure. You should also include a Where condition to target only the contributing lines. This approach maintains consistency when using the Map Line Item element in discovery procedures for derived pricing.

Use the Aggregate Price Element
Aggregate and show the price of a group of products based on product categories, product types, or other groups of line items.
Roll Up Pricing Using the Aggregate Price Element
Calculate the total price of a group of products using the Roll Up Price option using the Aggregate Price element. When you enable roll up price, the element first determines the price of each child product, and then, adds the total to a parent product.
