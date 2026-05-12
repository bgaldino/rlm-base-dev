---
article_id: ind.rm_element_negotiated_baserate_bindingobject.htm
title: Negotiated Base Rate for Binding Object
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_baserate_bindingobject.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Negotiated Base Rate for Binding Object

Use the Negotiated Base Rate element to calculate the negotiated target-specific rates. The negotiated base rate element uses the Binding Object Rate lookup table to determine if rates were negotiated. If rates weren't negotiated, the element uses base rates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Base Rate Variables

Map the variables in the Binding Object Rate 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Card Entry ID	BindingObject__std	The ID of the binding object rate card entry record that's related to the sellable product that the usage resource is associated with.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Negotiated Rate	Create a custom tag	The negotiated rate applied to the base rate of the usage resource under the asset.
Rate Card Entry: Rate	Create a custom tag	The original rate derived from the rate card entry.
Rate Card Entry: Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Base Rate Field	Predefined constant	The field name refers to the rate column of the selected base rate.
Quantity	OverageQuantity	Specify the quantity of the line items used in the transaction.
Negotiated Rate Field	Predefined Constant	The field name refers to the negotiated rate column of the selected base rate.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Base Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
