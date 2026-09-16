---
article_id: ind.rm_element_rate_adjustment_matrix_variables.htm
title: Rate Adjustment Matrix Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_rate_adjustment_matrix_variables.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_rate_adjustment_matrix.htm
fetched_at: 2026-09-07
---

# Rate Adjustment Matrix Variables

To calculate discounts, use the RateManagementContext context definition and relate it to a custom rate adjustment matrix.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Map the variables in the lookup table to the relevant context tags.

NOTE Based on your custom adjustment matrix, you can have dynamic input and output rule variables. In this task, we’re describing only the fixed input and output variables.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type Field	AttributeKey	The field name refers to the adjustment type column of the selected rate adjustment matrix.
Adjustment Value Field	AttributeValue	The field name refers to the adjustment value column of the selected rate adjustment matrix.
Quantity	OverageQuantity	Specify the quantity that’s consumed over the granted quantity.
Input Unit Rate	

NetUnitRate

This context tag is populated based on the output generated from the previous element.

	The rate details of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	NetUnitRate	The total rate of the usage resource.
Subtotal	TotalAmount	The subtotal rate for a usage resource.
