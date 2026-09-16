---
article_id: ind.rm_element_bora.htm
title: Get Binding Object Rate Adjustment
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_bora.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_discovery_procedure_elements.htm
fetched_at: 2026-09-07
---

# Get Binding Object Rate Adjustment

To retrieve the binding object rate adjustment ID(s) and map the variables to the relevant context tags, use the Binding Object Rate Adjustment Resolution Entries lookup table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	BindingObjectRateAdjustmentType__std	The adjustment type for the tier adjustment.
Adjustment Value	BindingObjectRateAdjustmentValue__std	The adjustment value for the adjustment type.
Binding Object Rate Adjustment ID	BindingObjectRateAdjustmentId__std	The ID of the binding object rate adjustment.
Lower Bound	BindingObjectRateAdjustmentLowerBound__std	The minimum number of units for a usage product.
Upper Bound	BindingObjectRateAdjustmentUpperBound__std	The maximum number of units for a usage product.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Card Entry ID	BindingObjectRateCardEntryId__std	The ID of the binding object rate card entry.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Adjustment ID	BindingObjectRateAdjustmentId__std	The ID of the binding object rate adjustment.

To retrieve the asset rate adjustment IDs and map the variables to the relevant context tags, use the Asset Rate Adjustment Resolution Entries lookup table.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Asset Rate Card Entry	AssetRateCardEntryId__std	The ID of the asset rate card entry.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	AssetRateAdjustmentType__std	The adjustment type for the tier adjustment.
Adjustment Value	AssetRateAdjustmentValue__std	The adjustment value for the adjustment type.
Asset Rate Adjustment ID	AssetRateAdjustmentId__std	The ID of the asset rate adjustment.
Lower Bound	AssetRateAdjustmentLowerBound__std	The minimum number of units for a usage product.
Upper Bound	Create a custom tag	The maximum number of units for a usage product.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Card Entry ID	AssetRateCardEntryId__std	The ID of the asset rate card entry.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Adjustment ID	AssetRateAdjustmentId__std	The ID of the asset rate adjustment.
