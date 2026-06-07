---
article_id: ind.pricing_pricing_element.htm
title: Use Pricing Elements in Pricing Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_element.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Use Pricing Elements in Pricing Procedures

Pricing elements are the fundamental building blocks used to construct a pricing procedure. Use these elements to define how prices are calculated and applied in Agentforce Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

When a pricing procedure is executed, most elements query relevant decision tables based on input parameters to retrieve pricing rules and values. Other elements rely on formulaic calculations, or assist with mapping relevant context tags within a procedure.

Pricing elements enable comprehensive and flexible pricing strategies. They ensure accurate pricing of products, whether in their simple form, using attributes as pricing parameters, or as complex product bundles. Furthermore, these elements facilitate the design of various product selling models, such as one-time sales or subscriptions. They also utilize price adjustment schedules to automatically adjust prices based on your unique pricing strategies, helping sales representatives offer their customers the best price for their products.

Map Context Tags in Pricing Procedure

Fetch the List Price of a Product
To get the base price of a product for pricing procedure execution, use the List Price element. The list price serves as a starting point for calculating the final price before applying any discounts or adjustments.
Volume and Tier Based Discounts
To calculate the price of a product based on discounts configured according to the quantities purchased, use the Volume Discount or the Tier Discount element.
Manually Discount Product Prices
Manual discounts, also known as discretionary discounts, can be applied to products to provide additional price reductions.
Attribute-Based Discounts
To calculate a product's price based on its associated attributes, use the Attribute-Based Price element.
Bundle-Based Price
Define and manage bundle-based discounts for a group of products that are sold as a unit.
Manage Pricing Using Proration and Subscription Elements
Use the Proration and Subscription elements in Salesforce Pricing to apply time-based pricing when a customer starts, cancels, or changes a subscription mid-cycle. These elements ensure customers are charged only for the time they ‌use your product or service.
Dynamic Pricing With Price Adjustment Matrix

Build Pricing Rules with Formula-Based Pricing
Perform functions and mathematical calculations to generate the price of a product. Solve complex pricing scenarios by defining multiple formulas within a single Formula-Based Pricing element.
List Group and List Operation
Efficiently process lists of data and implement complex pricing logic and calculations by enabling filtering, value lookups, and various computations on line items.
Map Context Tag Data Using Assignment Element
Dynamically set or change the values of pricing variables by mapping data between context tags or from a variable directly into a context tag.
Calculate Aggregate Prices for Products
Determine the aggregate prices of a group of products by defining aggregation at multiple line item layers and ensuring pricing is calculated at the configured levels.
Apply Price Rounding Values

Track Price Ranges for Products
Ensure transparent pricing policies and comply with regional directives by tracking a product's minimum and maximum prices over time using the Price Tracking element.
Stop Pricing
Use the Stop Pricing element to stop the execution of the pricing procedure for a particular line item. During simulation, the Waterfall view shows the element that the pricing procedure stopped at.
Price Propagation
Enable complex, hierarchical pricing logic by propagating values across different levels of a transaction from line items to groups and back. Use the Price Propagation element to perform sequential calculations and roll up totals from children to parents.
