---
article_id: ind.pricing_essentials.htm
title: Salesforce Pricing Essentials
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_essentials.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Salesforce Pricing Essentials

Browse through this collection of terms, key objects, and key concepts. This collection is designed to give Salesforce admins, sales reps, and developers a clear and consistent understanding of pricing concepts and helps them navigate the Salesforce Pricing landscape.

Aggregate Price
Aggregate Price is the pricing element that allows users to combine or aggregate prices based on a specific set of rules for multiple products within a transaction.
Assignment Element
Assignment element is the pricing element used to assign values from one context tag to another based on business needs.
Attribute-Based Adjustment
Attribute-Based Adjustment refers to a definition where a product is eligible for discounts if its attribute values meet certain criteria within a specified time frame. You can define this rule for multiple products.
Attribute-Based Price
Attribute-Based Price is the pricing element where attribute-based discounts are applied to a product if the product meets the eligibility criteria, and calculations are performed accordingly.
Bundle-Based Adjustment
Bundle-Based Adjustment refers to a definition where a product is eligible for discounts if it’s part of a specific bundle within a designated time frame. You can define this rule for multiple products.
Bundle-Based Price
Bundle-Based Price is the pricing element where bundle-based discounts are applied to a product if the product meets the eligibility criteria, and calculations are performed accordingly.
Contract-Based Pricing
Contract-Based Pricing is a pricing element that determines prices based on a specific contract associated with a product in a transactionThis pricing type is applied only when the Use Contract-based Pricing option is enabled for the pricing element.
Cost Book
A cost book is a centralized storage location where a group of products and their base costing details are defined.
Cost Book Entry
A cost book entry defines each product's cost during a specific time frame.
Cumulative Quantity Pricing
Apply Cumulative Pricing to generate discounts for both volume and tier-based quantities of different line items, including historical purchases.
Delta Pricing
Use Delta Pricing to reprice only the modified line items in quotes and orders.
Derived Pricing
Derived Pricing calculates the price of a product based on the prices of another set of products, headers, or historical prices—both transactional and non-transactional—of those products.
Discount Distribution Service
The Discount Distribution Service makes sure that discounts are applied fairly across qualifying line items. You can also set floor price limits to protect profit margins and exclude specific products or categories from discount spreads.
Discovery Pricing Procedure
The Discovery Pricing Procedure is another pricing procedure that determines the set of assets required to derive the pricing of a product. This procedure is primarily intended for derived pricing use cases.
Element Parallelisation
Use Parallel Element Execution to process elements concurrently during the execution of a pricing procedure. This improves the performance of pricing APIs and their simulations.
Formula Pricing
Formula Pricing is the pricing element that allows users to define a custom pricing formula that they can apply to the prices of specified products.
Get List Price
Get List Price is the pricing element where the base price of a product is calculated in the pricing procedure.
List Group
The List Group is part of the pricing procedure where you can establish specific conditions, and define a set of pricing elements based on these rules.
List Price
The List Price is the pricing element that calculates the base price of a product within the pricing procedure.
Manual Discount
Manual Discount refers to the pricing element where any manual adjustments such as percentage, amount, or override, are applied to a product during a specific transaction. This discount is applied at run time and isn't established during the definition phase.
Map Line Items
Map Line Items is a pricing element that maps a parent to a child node in the context definition. It's primarily used to define pricing for the breakdown lines and calculate the sublines in amend, renew, and cancel scenarios.
Pricing Action
Pricing Action is a pricing feature that allows users to define context definitions and pricing procedures to execute any object. You can apply this feature to any Salesforce object in Salesforce for price calculation. Users can create custom context definitions, establish pricing procedures, and use pricing actions to price any item.
Price Adjustment Matrix
The Price Adjustment Matrix is a pricing element that executes ‌custom pricing rules, enabling adjustments to be applied to a specific product.
Price Adjustment Schedule
The Price Adjustment Schedule is a grouping mechanism that users can define adjustments for a specific set of products, categorized based on type Volume, Attribute, Custom, and Bundle. You can also define this group within a specific time frame during which all adjustments can be leveraged.
Price Adjustment Tier
The Price Adjustment Tier defines volume-based adjustments, enabling users to define the adjustment such as Percentage, Amount, Override for a specific quantity range. If the product's quantity falls within this range during a specified time frame, the product becomes eligible for discounts. You can define this rule by using the Price Adjustment Tier.
Price Book
A centralized storage location where a group of products and their base prices are defined.
Price Book Entry
A price book entry defines each product's base price or list price. This price can also be considered the starting price.
Price Revision
The Price Revision element applies an appropriate price revision policy to adjust the price of a product using formulas based on various price adjustments.
Price Revision Policy
Represents the guidelines and methods used to modify product or service prices, often incorporating formulas based on price revision entries and various adjustments.
Procedure Output Resolution
Use Procedure Output Resolution to determine the best price for a product when a pricing rule produces multiple outcomes. The resolution can be applied to list price and price tracking elements.
Pricing Discount Calendar
The Pricing Discount Calendar shows all discounts and adjustments for a product over specific time frames. You can view and edit the details of individual discounts.
Pricing Element
A Pricing Element is a structure within a Pricing Procedure. Each pricing solution is represented as a pricing element that you can drag and drop to address various business use cases.
Pricing Operations Console
The Pricing Operations Console helps your company use price logs to troubleshoot and resolve issues caused by pricing APIs.
Pricing Procedure
A Pricing Procedure is the price orchestration or pricing policy that users can define how to price their products or services. Users can also define custom logic and solutions to implement pricing strategies in any org.
Pricing Propagation
The Propagation element automatically applies discounts, margins, and custom calculations from groups to line items and rolls them up into accurate totals.
Pricing Recipe
A Pricing Recipe is a collection of decision tables used in pricing procedures for pricing calculations.
Pricing Simulation
Pricing Simulation is a feature that users can simulate the orchestration and pricing policy after they set up a Pricing Procedure. By using real data and validating the pricing waterfall, users can determine the expected price and discount for products, as well as validate the procedure.
Price Waterfall
Price Waterfall provides detailed information about the outcome of pricing execution for any transaction. It outlines the step-by-step process of how the products or services are priced and details any discounts or adjustments that the transaction underwent.
Procedure Plan Framework
The Procedure Plan Framework, serves as a one-stop solution where users can define the context for an end-to-end transaction and also define multiple procedures based on Qualification, Pricing, and Asset Discovery rules.
Promotion Execution
The Promotion element evaluates and applies promotion-based discounts to transaction lines during the pricing process.
Propagation table
The Propagation Table is a calculation table used to set up formulas for quote line item and group level fields, define group level aggregates across the nested structure, and define the sequence of execution.
Proration Element
The Proration element determines the proration value of a product for a specific time period and specific terms and term units.
Subscription Pricing
Subscription Pricing is the pricing element that calculates the subscription price of a product by considering the proration value.
Tiered Discount
Tiered Discount is the pricing element where tiered adjustments, also known as slab-based discounts, are calculated for products in the pricing procedure.
Volume Discount
Volume Discount is the pricing element where volume-based adjustments are calculated for products in the pricing procedure.
