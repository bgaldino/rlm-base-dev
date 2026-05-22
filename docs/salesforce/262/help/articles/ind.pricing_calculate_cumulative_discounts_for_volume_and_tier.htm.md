---
article_id: ind.pricing_calculate_cumulative_discounts_for_volume_and_tier.htm
title: Cumulative Pricing Using Volume or Tier Discount Elements
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_cumulative_discounts_for_volume_and_tier.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Cumulative Pricing Using Volume or Tier Discount Elements

Customers can apply volume or tier-based discounts to a line item based on aggregated product quantities, whether from past purchases (asset quantity) or multiple line items within the same quote or order.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

This ability to aggregate quantities, from current transactions or historical purchases, is crucial for effective discounting. It allows customers to receive cumulative quantity discounts based on defined rules, incentivizing larger purchases over time and honoring negotiated pricing commitments.

By using cumulative pricing, discounts are applied based on the total quantity from past purchases or multiple line items within the same transaction, rather than just individual line item quantities. This method ensures that the pricing engine considers the full scope of a customer's purchasing activity when calculating discounts.

Applying Cumulative Quantity to Volume Discounts

When you apply cumulative pricing to the Volume Discount element, the transaction system provides the aggregated quantity, which the pricing engine then utilizes.

For example, if the aggregated quantity from past purchases is 6 units and the current line item quantity is 2 units, the total cumulative quantity becomes 8 units. If your discount tier offers 10% off for 5-10 units, this discount will be applied to the currently purchased 2 units, even though only 2 items were purchased in the current transaction.

Applying Cumulative Quantity to Tier Discounts

Similarly, when you apply cumulative pricing to the Tier Discount element, it exposes the Cumulative Tier Quantity input variable. This input variable is mapped to a context tag and passed by the transaction system. This value helps the pricing engine determine which tiers are relevant.

For example, let’s assume that the cumulative tier quantity is 3 units, and the current line item quantity is 6 units. If your pricing structure has an initial tier with no discount for 1 to 3 units, this tier would be filled by the cumulative quantity of 3. The current line item quantity of 6 would then be spread across subsequent tiers such as, 4-7 units and 8-10 units, potentially leading to a higher overall discount than if only the line item quantity was considered.

NOTE For active orders or assets, cumulative pricing requires Contract Pricing Volume or Tiered Discounts. However, when simulating a pricing procedure, you can use cumulative quantity independently, without Contract Pricing.
