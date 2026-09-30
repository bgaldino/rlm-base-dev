---
article_id: release-notes.rn_transaction_management_ramp_deal_compound_uplift.htm
title: Apply Compound Price Uplifts to Multiyear Ramp Deals to Adjust Pricing Over Time
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_ramp_deal_compound_uplift.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_ramp_deals.htm
fetched_at: 2026-09-30
---

# Apply Compound Price Uplifts to Multiyear Ramp Deals to Adjust Pricing Over Time

Select between standard and compound uplift modes for multiyear ramp deals. Standard uplift applies a fixed percentage against the original list price for every segment. Compound uplift builds each segment's price on the net price from the prior segment to match the annual escalation pattern common in enterprise contracts.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

Why: Multiyear enterprise deals often include annual price escalations that compound pricing. Each year's increase builds on the actual price from the prior year, not the original list price. Previously, the ramp uplift in Revenue Cloud was in standard mode. Sales teams calculated compound prices manually, which raised the risk of quoting errors and made deal approvals slower.

With compound uplift, the pricing engine calculates and applies the correct compounded percentage for each segment automatically. The price waterfall now shows the applied unit price uplift percentage for every segment. Sales teams have a clear record of each segment's price calculation.

How: To configure the default ramp uplift type, from Setup, in the Quick Find box, enter Revenue Settings, and then select Revenue Settings. Turn on Advanced Detail Line Pricing. Then, set the default ramp uplift type to standard or compound uplift.
