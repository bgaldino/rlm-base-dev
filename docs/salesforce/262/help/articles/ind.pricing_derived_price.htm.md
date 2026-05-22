---
article_id: ind.pricing_derived_price.htm
title: Implement Derived Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_derived_price.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Implement Derived Pricing

To accurately calculate a product’s price from another pricing source, such as a product or an asset, or the overall quote value, use the Derived Price feature.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

Derived pricing functions by establishing clear relationships between a derived product (the product whose price is being calculated) and a source for that calculation. This source can be a source product (providing the basis for the calculation) or even the aggregate value of the entire transaction.

Before you begin implementing derived pricing, it's crucial to understand these key concepts:

The Pricing Source indicates where the pricing information originates.

PRICING SOURCE	DESCRIPTION
Product	The price is derived from one or more specific products within a transaction.
Header	The price is derived from the total cost of all products in the transaction cart.

The Pricing Scope determines the method by which the derived price is calculated, and your choice depends on the selected pricing source.

PRICING SCOPE	DESCRIPTION
Transactional	The price is derived from one or more specific products within a transaction.
Non-transactional	The price is derived from the total cost of all products in the transaction cart.
Both	Allows for a combination of both transactional and non-transactional scopes.

By setting up your derived products and defining specific pricing rules and formulas, the system automatically determines their price when added to a quote or order. This eliminates manual calculations, reduces errors, and allows for flexible, automated pricing that adapts to various business needs.

Prerequisites to Build Discovery and Derived Price Pricing Procedures
Before you begin creating discovery procedures to locate pricing data for your products and assets, or to calculate a product’s derived price, ensure you have completed the following prerequisites. A fundamental understanding of these concepts is crucial for the successful implementation and operation of your pricing strategies.
Discover Pricing Factors

Calculate the Derived Price of Product
Use the discovery procedure and the derived price element in a pricing procedure, to calculate a product’s price from another product or asset.
