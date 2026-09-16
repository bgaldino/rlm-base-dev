---
article_id: ind.pricing_discovery_procedure_for_pricing.htm
title: Discover Pricing Factors
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_discovery_procedure_for_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_derived_price.htm
fetched_at: 2026-09-07
---

# Discover Pricing Factors

To accurately calculate a product's derived price, discovery procedures gather contributing factors and store them within a defined context definition, ensuring precise data access.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

Derived pricing often requires specific, disparate data from various sources like products, assets, or quotes. Discovery procedures are essential for finding, collecting, and organizing this vital information into a structured format, making it readily available for the pricing engine.

Understand Discovery Procedure Elements

Every discovery procedure comes with three default elements, each serving a distinct purpose in locating pricing data for products or assets. Configuring a discovery procedure is the crucial first step in calculating a product's derived price.

DISCOVERY ELEMENT	DESCRIPTION
Fetch Pricing Rules	Retrieves derived pricing rules from the Derived Pricing Entries decision table and writes them to the context definition's Contributor node. The Contributor node stores the product IDs, formulas, scope (transactional or non-transactional), and source (header or product) needed to calculate derived prices.
Map Product	Matches contributing products from the fetched pricing rules with products on the current quote or order. If conditions are specified, only matching products are selected. If no conditions are specified, all contributing products present in both the pricing rules and the quote are selected.
Asset Discovery	Used for non-transactional derived pricing calculations. Retrieves pricing data from the customer's existing assets by querying the Asset Action Source Entries V2 decision table for each contributing product's active assets. The calculated prices are stored in the context definition's Contributor node for use in the pricing procedure. Product2Id is automatically passed from the Contributor node populated by Map Product.

Beyond the default elements, you can use the Map Line Item element in your discovery procedure to map tags for individual line item details using parent tags. When doing so, ensure that the Discovery Settings element is placed first, immediately followed by the Map Line Item element. For more information, refer to the Map Line Item section in Map Context Tags in Pricing Procedures.

Configure a Discovery Procedure
To calculate a product's derived price, configure a discovery procedure with the elements required to gather all contributing factors.
