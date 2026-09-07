---
article_id: ind.rm_element_negotiated_base_rate.htm
title: Negotiated Base Rate
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_base_rate.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Negotiated Base Rate

To calculate the negotiated rates applied on the base rate of the usage resource, use the Negotiated Base Rate element. The negotiated base rate element uses the Asset Rate lookup table to determine if rates were negotiated. If rates weren't negotiated, the element uses base rates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Base Rate Variables

Map the variables in the Asset Rate 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Asset Rate Card Entry ID	Asset	The ID of the asset record that's related to the sellable product that the usage resource is associated with.
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
Add the Negotiated Base Rate Element
Here’s how you can add the Negotiated Base Rate element to your rating procedure.
