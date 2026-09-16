---
article_id: ind.rm_element_negotiated_tierbased_adjustment.htm
title: Negotiated Tier-Based Rate Adjustment
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_tierbased_adjustment.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Negotiated Tier-Based Rate Adjustment

The Negotiated Tier-Based Rate Adjustment element calculates the negotiated rate for a usage resource based on the defined tiers, applying either a discount or a surcharge.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
EXAMPLE Let’s assume that you’re consuming 100-GB data for your organization. The unit rate of 1-GB data is US$0.5, and your service provider offers you these tier-based discounts.
No discount for data consumption of fewer than 10 GB.
1% discount for each GB consumed when 11–60 GB of data is consumed.
2% discount for each GB consumed when 61–100 GB of data is consumed.

Here’s how the post-negotiation, the discounts are applied and the total amount is calculated.

QUANTITY	POST NEGOTIATION	TOTAL
RATE
First 10 GB	No discounts applied for the first 10 GB	10 x 0.5 = $5
Next 50 GB	10% off for licenses 11–60 GB	50 x 0.45 = $22.5
Last 40 GB	20% off for licenses 61–100 GB	40 x 0.4 = $16
Negotiated Tier-Based Adjustment Variables
Map the variables in the Asset Tier-Based Rate Adjustment 2 lookup table to the relevant context tags.
Add Negotiated Tier-Based Rate Adjustment
Here’s how you can add the Negotiated Tier-based Rate Adjustment element to your rating procedure.
