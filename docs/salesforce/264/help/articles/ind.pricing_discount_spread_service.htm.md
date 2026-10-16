---
article_id: ind.pricing_discount_spread_service.htm
title: Discount Distribution Service
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_discount_spread_service.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_unique_pricing_scenarios.htm
fetched_at: 2026-09-07
---

# Discount Distribution Service

Apply quote-level discounts across each line item ensuring consistent and accurate pricing using the Discount Distribution Service feature in Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

During certain sales deals, sellers want to apply discretionary discounts at the quote total level, also known as header level. When these discounts are applied to the header by a sales rep, the individual line items within the quote or quote line group must be adjusted as well to ensure accounting accuracy and facilitate reconciliation. The Discount Distribution Service ensures that these discounts are applied correctly across qualifying line items.

Additionally, you can set floor price limits to safeguard profit margins and even exclude certain products or categories from discount distributions, giving you precise control over your discounting strategy.

What is Floor Price Limit?

Floor price limits represent the minimum prices a business establishes for its products, effectively preventing any discounts or price reductions from being applied below this pre-defined threshold.

This safeguards profit margins and maintains pricing integrity. These limits apply when the discount distribution is set to Net Unit Price, and any unapplied discount amounts are tracked in the Total Remainder Amount.

You can implement these limits by either including them in your context definition or creating a custom object for them and hydrating it with a Context Service. Both methods ensure that even with discretionary discounts, your profitability is protected.

EXAMPLE If the floor price limit for a mobile phone is $500 USD and a discount reduces the price to $400, the service preserves the floor price limit of $500. The remaining amount is applied to the next eligible line item. If no line items are available, any remaining amount is saved in the Total Remainder Amount tag.
Discount Distribution Service Limits

Before adding the Discount Distribution Service element to your pricing procedure, keep the following points in mind.

The Discount Distribution Service element must be the last element in the pricing procedure.
The element can only be used once within a single pricing procedure.
You can’t apply discount distribution to a pricing procedure that was used to calculate a product's derived price.
Floor price limits are only applied when the distribution type is set to the NetUnitPrice variable.
Amend and renew processes don’t account for intended price values, as they assume that (NetUnitPrice * Quantity = ItemNetTotal). In the Discount Distribution Service element, when a discount is applied to ItemNetTotal, the NetUnitPrice isn't recalculated; it’s intended as a one-time discount.
While Proration and Subscription elements update the LineItemSubTotal variable by multiplying the ProrationMultiplier with the NetUnitPrice tag, the Discount Distribution Service only utilizes the NetUnitPrice variable for its pricing calculations.
If you intend to use the total subscription price, use a Formula element and provide the formula - Proration Multiplier * NetUnitPrice. Then, use the output of this formula as the InputPrice variable for calculations within the Discount Distribution Service element.
Understand Discount Distribution Service Terms
Familiarize yourself with the variables and terminology you'll encounter when you configure a pricing procedure to calculate discounts using the Discount Distribution Service element.
Use the Discount Distribution Service Element
To calculate discounts that can be spread evenly across all line items or specifically across a subsection of line items, use the Discount Distribution Service element.
Discount Distribution Service Limits
Before adding the Discount Distribution Service element to your pricing procedure, keep these points in mind:
