---
article_id: ind.rm_negotiated_volumebased_rate_adjutment_variables.htm
title: Negotiated Volume-Based Rate Adjustment Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_negotiated_volumebased_rate_adjutment_variables.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_negotiated_volumebased_rate_adjustment.htm
fetched_at: 2026-09-07
---

# Negotiated Volume-Based Rate Adjustment Variables

Map the variables in the Asset Volume-based Rate Adjustment 2 lookup table to the relevant context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG DESCRIPTION
Asset Rate Card Entry: Asset ID	BindingObjectTierRateCardEntry__std	The ID of the Binding Object Rate Card Entry of type Tier.
Lower Bound	OverageQuantity	The minimum number of units for a usage product for a tier.
Upper Bound	OverageQuantity	The maximum number of units for a usage product for a tier.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	Create a custom tag	Enter the adjustment type applicable to the usage resource.
Adjustment Value	Create a custom tag	Enter the adjustment value applicable to the usage resource.
Rate Card Entry: Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Quantity	OverageQuantity	Specify the quantity that’s consumed over the granted quantity.
Input Unit Rate	NetUnitRate	The rate details of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
Is Tier Negotiated	IsTierNegotiated	Specify whether the Rate Card Entry of type Tier is negotiated.
