---
article_id: ind.rm_element_negotited_volumebasedadjustment_bindingobject.htm
title: Negotiated Volume-Based Rate Adjustment for Binding Object
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotited_volumebasedadjustment_bindingobject.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Negotiated Volume-Based Rate Adjustment for Binding Object

Use the Negotiated Volume-Based Rate Adjustment element to fetch the volume-based rate adjustment related to the binding object ID specified in the decision table along with other input values.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Volume-Based Adjustment Variables

Map the variables in the Binding Object Volume-Based Rate Adjustment 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
 	 	 
Binding Object Rate Card Entry ID	BindingObjectTierRateCardEntry__std	The ID of the rate card entry of type Tier.
Lower Bound	OverageQuantity	The minimum number of units for a usage product.
Upper Bound	OverageQuantity	The maximum number of units for a usage product.
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
