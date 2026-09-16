---
article_id: ind.rm_element_get_tier_based_rate_adjustments.htm
title: Get Tier-Based Rate Adjustments
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_get_tier_based_rate_adjustments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_discovery_procedure_elements.htm
fetched_at: 2026-09-07
---

# Get Tier-Based Rate Adjustments

Select the Rate Adjustment by Tier Resolution Entries lookup table to fetch the tier-based adjustments, and then map the variables to the relevant context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	TierAdjustmentType	The adjustment type for the tier adjustment.
Adjustment Value	TierAdjustmentValue	The adjustment value for the adjustment type.
Rate Adjustment By Tier ID	RateAdjustmentByTierID	The ID of the rate adjustment by tier record associated with the rate card entry.
Lower Bound	TierLowerBound	The minimum number of units for a usage resource.
Upper Bound	TierUpperBound	The maximum number of units for a usage resource.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Entry ID	RateCardEntryId	The ID of the rate card entry.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Adjustment By Tier ID	RateAdjustmentByTierID	The ID of the rate adjustment by tier record.
