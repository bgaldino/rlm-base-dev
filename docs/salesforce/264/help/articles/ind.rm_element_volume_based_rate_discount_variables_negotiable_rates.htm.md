---
article_id: ind.rm_element_volume_based_rate_discount_variables_negotiable_rates.htm
title: Volume-Based Rate Discount Variables for Negotiable Rates
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_volume_based_rate_discount_variables_negotiable_rates.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_volume_based_rate_discount.htm
fetched_at: 2026-09-07
---

# Volume-Based Rate Discount Variables for Negotiable Rates

To calculate negotiable rates, relate the Volume-Based Rate Discount element with the Volume-based Rate Adjustment by Rate Card Entry ID lookup table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Map the variables in the lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Entry	TierRateCardEntry	The ID of the selected rate card entry of type tier.
Lower Bound	OverageQuantity	The minimum number of units for a usage product for a tier.
Upper Bound	OverageQuantity	The maximum number of units for a usage product for a tier.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	Create a custom tag	The adjustment type.
Adjustment Value	Create a custom tag	The adjustment value.
Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Quantity	OverageQuantity	Specify the quantity that’s consumed over the granted quantity.
Input Unit Rate	

NetUnitRate

This context tag is populated based on the output generated from the previous element.

	The rate details of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
