---
article_id: ind.pricing_procedure_output_resolution.htm
title: Establish Procedure Output Resolution
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_procedure_output_resolution.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Establish Procedure Output Resolution

To select the definitive price for a product when pricing rules generate multiple outcomes, implement Procedure Output Resolution.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

To determine the best price, you must first configure your pricing strategies and then select the option to enable output resolution within a pricing element of a pricing procedure. There are four common best price practices that we can determine using the Procedure Output Resolution feature.

Minimum Price: The lowest price available for the selected product.
Maximum Price: The highest price available for the selected product.
Stack: The application of discounts cumulatively for a product.
Sequence: The application of discounts individually, one after another, for a product.

Procedure output resolution elegantly handles scenarios where a single product has multiple potential prices. This complexity arises whether a product, like a laptop, is listed in several price books with different list prices, or when various adjustments like volume discounts and promotions stack on top of each other to create conflicting calculations. To solve this, you define a single resolution strategy to automatically determine the final price. For instance, a strategy can be set to simply select the lowest (minimum) or highest (maximum) price from all possibilities, or it can apply the adjustments sequentially based on a specific priority, ensuring a predictable and accurate final price is always offered to the customer.

Currently, Salesforce Pricing only supports output resolution in the List Price, Price Tracking, and Price Adjustment Matrix elements. The Stack and Sequence formula options appear only when you use the Price Adjustment Matrix element of a pricing procedure.

NOTE When you enable multi-output resolution for a List Price or Price Tracking element, make sure that every product has a matching entry in the Price Book (Decision Table). If the pricing engine doesn't find any matching records, the element treats this as a configuration error and stops the pricing process for that line item. The element doesn't default to zero or skip the step.
Understand Your Resolution Variables
When you enable output resolution in your pricing element, you’ll see a new Resolution Variables section that will consume the details of the resolution strategy you’ve created. The variables in the Resolution Variables section must be mapped to accurate context tags.
Configure Pricing Resolution Strategies
To set a pricing resolution strategy, create a procedure output resolution record.
Determine the Best Price for a Product Using Pricing Procedures
Use a pricing procedure to determine the best price for a product using a resolution strategy when multiple pricing options exist.
