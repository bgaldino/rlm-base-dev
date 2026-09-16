---
article_id: ind.rm_element_negotiated_tierbased_rate_adjustment.htm
title: Negotiated Tier-Based Adjustment Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_tierbased_rate_adjustment.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_negotiated_tierbased_adjustment.htm
fetched_at: 2026-09-07
---

# Negotiated Tier-Based Adjustment Variables

Map the variables in the Asset Tier-Based Rate Adjustment 2 lookup table to the relevant context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT
TAG
DESCRIPTION
Asset ID	Asset	The ID of the asset record that's related to the sellable product with which the usage resource is associated.
Rate Card Entry ID	

TierRateCardEntry

This context tag is populated based on the output generated from the Negotiated Rate Card Entries element.

	The ID of the Rate Card Entry of type tier.
Start Date	RatingDecisionDateTime	The start date of the transaction.
End Date	RatingDecisionDateTime	The end date of the transaction.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	Create a custom tag	The adjustment type.
Adjustment Value	Create a custom tag	The adjustment value.
Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Quantity	OverageQuantity	Specify the quantity of the line items used in the transaction.
Input Unit Rate	NetUnitRate	The rate details of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
Is Tier Negotiated	IsTierNegotiated	Specify if the Rate Card Entry of type tier is negotiated.
