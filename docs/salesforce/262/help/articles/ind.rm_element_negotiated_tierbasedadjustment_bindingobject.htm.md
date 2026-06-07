---
article_id: ind.rm_element_negotiated_tierbasedadjustment_bindingobject.htm
title: Negotiated Tier-Based Rate Adjustment for Binding Object
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_tierbasedadjustment_bindingobject.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Negotiated Tier-Based Rate Adjustment for Binding Object

Use the Negotiated Tier-Based Rate Adjustment element to fetch the tier-based rate adjustment with bound range related to the binding object ID specified in the decision table along with other input values.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Tier-Based Adjustment Variables

Map the variables in the Binding Object Tier-based Rate Adjustment 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Card Entry: Binding Object ID	BindingObject__std	The ID of the binding object record that's related to the sellable product that the usage resource is associated with.
Rate Card Entry ID	TierRateCardEntry	The ID of the Rate Card Entry of type Tier.
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
Is Tier Negotiated	IsTierNegotiated	Specify if the Rate Card Entry of type Tier is negotiated.
