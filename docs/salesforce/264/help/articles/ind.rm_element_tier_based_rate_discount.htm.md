---
article_id: ind.rm_element_tier_based_rate_discount.htm
title: Tier-Based Rate Discount
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_tier_based_rate_discount.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Tier-Based Rate Discount

The Tier-Based Rate Discount element determines the discount for a usage resource based on the quantity consumed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

The tier-based rate discount element is similar to the volume-based rate discount element in terms of usage. The primary difference is that a standard flat discount rate is applied to all usage resources when you use the volume-based rate discount element. When you use the tier-based rate discount method, you define a range-based discount for the usage resource based on the quantity consumed.

EXAMPLE Let’s assume that you’re consuming 100-GB data for your organization. The unit rate of 1-GB data is US$0.5, and your service provider offers you these tier-based discounts.
No discount for data consumption of fewer than 10 GB.
10% discount for each GB data consumed when 11–60 GB are consumed.
20% discount for each GB data consumed when 61–100 GB are consumed.

Here’s how the discounts are applied, and the total amount is calculated.

QUANTITY	DISCOUNTS APPLIED	TOTAL RATE
First 10 GB	No discounts applied for the first 10 GB	10 x 0.5 = $5
Next 50 GB	10% off for licenses 11–60 GB	50 x 0.45 = $22.5
Last 40 GB	20% off for licenses 61–100 GB	40 x 0.4 = $16
Add the Tier-Based Rate Discount Element
Here’s how you can add the Tier-Based Rate Discount element to your rating procedure.
