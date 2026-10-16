---
article_id: ind.pricing_add_the_price_adjustment_matrix_element.htm
title: Dynamic Pricing With Price Adjustment Matrix
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_add_the_price_adjustment_matrix_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Dynamic Pricing With Price Adjustment Matrix

Determine custom discounts and adjustments that go beyond the predefined options provided by Salesforce Pricing using Price Adjustment Matrix element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

The Price Adjustment Matrix element helps businesses set dynamic prices. It goes beyond simple volume discounts, letting you create complex pricing rules for different sales situations. This can be done by creating custom decision tables that hold pricing criteria and adjustments with or without custom objects. This allows for contextual pricing, tailoring offers based on quote details, customer info, or product features, ensuring precise, scenario-based pricing.

Implementing this framework involves a few key steps.

Create custom objects or use existing Salesforce objects to hold your price adjustment data.
Define decision tables, setting criteria (like quantity or product attributes) and their adjustments (discounts or price overrides).
Integrate these tables into your pricing procedure, linking them to relevant quote fields.
Finally, when processing a quote, the quoting system uses this information to dynamically calculate and apply accurate price adjustments.
Calculate Product Prices Using Price Adjustment Matrix
Let's look at a scenario where we want to apply custom percentage-based discounts using the Price Adjustment Matrix element.
