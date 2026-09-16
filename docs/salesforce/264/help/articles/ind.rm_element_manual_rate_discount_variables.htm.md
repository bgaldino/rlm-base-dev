---
article_id: ind.rm_element_manual_rate_discount_variables.htm
title: Manual Rate Discount Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_manual_rate_discount_variables.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_manual_rate_discount.htm
fetched_at: 2026-09-07
---

# Manual Rate Discount Variables

To calculate discounts, use the RateManagementContext context definition and map the variables to the relevant context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Map the variables in the lookup table to the relevant context tags.

Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	Create a custom tag	The adjustment type.
Adjustment Value	Create a custom tag	The adjustment value.
Quantity	OverageQuantity	Specify the quantity that’s consumed over the granted quantity.
Input Unit Rate	

NetUnitRate

This context tag is populated based on the output generated from the previous element.

	The rate details of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
