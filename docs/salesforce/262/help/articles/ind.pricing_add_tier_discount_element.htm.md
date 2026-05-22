---
article_id: ind.pricing_add_tier_discount_element.htm
title: Understand the Difference Between Volume and Tier Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_add_tier_discount_element.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Understand the Difference Between Volume and Tier Discounts

Distinguishing between volume and tiered discounts is crucial for applying the most effective pricing strategies to your products. Both methods allow you to offer discounts based on quantity purchased, often within specified date ranges, and can be integrated into your pricing engine.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
Volume Discounts
Provides a single, reduced price per unit once a customer reaches a specified quantity threshold. For example, if a customer buys 60 units and the volume discount activates at 40 units, all 60 units will be priced at the lower rate. This method offers a simple and straightforward way to apply discounts based on the total quantity purchased.
Tiered Discounts
Provides different price points to different quantity ranges. This offers more granular control over pricing, as the price per unit can change multiple times within a single purchase.

Let's illustrate with an example:

Imagine you're purchasing 25 laptops for your organization, with a unit price of $200 USD. Your manufacturer offers the following tier-based discounts.:

No discount for fewer than 10 laptops.
10% discount for every laptop when 10–19 laptops are purchased.
15% discount for every laptop when 20–29 laptops are purchased.

All tiers are included to calculate the price. Here’s how the discounts are applied and the total price is calculated for 25 laptops.

QUANTITY	DISCOUNTS APPLIED	TOTAL PRICE
For 25 laptops	

No discounts applied for the first 9 laptops

10% off for laptops 10–19

15% off for laptops 20–25

	(9 x $200) + (10 x $180) + (6 x $170) = $4620

To conclude, volume discounts offer one reduced price for all units once a quantity threshold is met, while tiered discounts apply progressively lower prices to units as the quantity purchased increases across different ranges.
