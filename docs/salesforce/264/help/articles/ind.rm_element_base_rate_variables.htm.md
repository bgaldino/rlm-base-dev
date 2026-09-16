---
article_id: ind.rm_element_base_rate_variables.htm
title: Base Rate Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_base_rate_variables.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_base_rate.htm
fetched_at: 2026-09-07
---

# Base Rate Variables

To monitor rates, use the RateManagementContext context definition and associate the Base Rate element with the Rate Card Entries lookup table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Map the variables in the lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card	BaseRateCard	The ID of the rate card of type base.
Usage Resource	UsageResource	The ID of the usage resource.
Product	SellableProduct	The ID of the sellable product related to the usage resource.
Rate Unit Of Measure	NetUnitRateUom	The standard unit of measure related to the rate card.
Product Selling Model	ProductSellingModel	The method used to sell a product.
Effective From	RatingDecisionDateTime	The start date of the transaction.
Effective To	RatingDecisionDateTime	The end date of the transaction.
Status	Predefined Constant	Specify whether the rate card entry is draft, active, or inactive.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate	Create a custom tag	Enter the base rate applicable to the usage resource.
Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Quantity	OverageQuantity	Specify the quantity of the line items used in the transaction.
Base Rate Field	Predefined constant	The field name refers to the rate column of the selected base rate.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Base Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
