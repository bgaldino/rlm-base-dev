---
article_id: ind.rm_element_get_borce.htm
title: Get Binding Object Rate Card Entries
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_get_borce.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_discovery_procedure_elements.htm
fetched_at: 2026-09-07
---

# Get Binding Object Rate Card Entries

To retrieve the binding object rate card entry IDs and map the variables to the relevant context tags, use the Binding Object Rate Card Entry Resolution Entries 2 lookup table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Usage Resource	FilterNodeUsageResourceId__std	The ID of the usage resource related to the binding object rate card entry.
Rate Unit Of Measure	FilterNodeRateUnitofMeasureId__std	The unit of measure of the rate defined for the usage resource.
Effective From	FilterNodeEffectiveFrom__std	The date when the binding object rate card entry becomes active.
Effective To	FilterNodeEffectiveFrom__std	The date when the binding object rate card entry becomes active.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Order	Create a custom tag	It determines the applicable binding object rate when multiple rates are defined for an Anchor target within an effective period.
Binding Object Rate Card Entry ID	BindingObjectRateCardEntryRateCardId__std	The ID of the binding object rate card entry.
Negotiated Rate	BindingObjectRateCardEntryNegotiatedRate__std	The negotiated rate associated with the binding object rate card entry.
Rate Card Type	BindingObjectRateCardEntryRateCardType__std	The type of rate card, such as attribute or tier.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object ID	FilterNodeBindingObjectId__std	The ID of the binding object related to the rate card entry.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Entry ID	RateCardEntryId	The ID of the rate card entry associated with the binding object.
Binding Object Rate Card Entry ID	BindingObjectRateCardEntryId__std	The ID of the binding object rate card entry.

To retrieve the asset rate card entry IDs and map the variables to the relevant context tags, use the Asset Rate Card Entry Resolution Entries lookup table.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Formula	FilterNodeBindingObjectId__std	The formula that returns the ID of the associated binding object, if specified. If binding object isn't added, the formula returns the asset ID of the asset related to this asset rate card entry.
Usage Resource ID	FilterNodeUsageResourceId__std	The ID of the usage resource related to the binding object rate card entry.
Start Date	FilterNodeEffectiveFrom__std	The date when the binding object rate card entry becomes active.
End Date	FilterNodeEffectiveFrom__std	The date when the binding object rate card entry becomes active.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Order	Create a custom tag	It determines the applicable binding object rate when multiple rates are defined for an Anchor target within an effective period.
Asset Rate Card Entry ID	AssetRateCardEntryId__std	The ID of the asset rate card entry.
Negotiated Rate	AssetRateCardEntryNegotiatedRate__std	The negotiated rate associated with the asset rate card entry.
Rate Card Type	Create a custom tag	The type of rate card, such as Base and Tier.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object ID	FilterNodeBindingObjectId__std	The binding object associated with the asset rate card entry.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Entry ID	RateCardEntryId	The ID of the rate card entry.
Binding Object Rate Card Entry ID	AssetRateCardEntryId__std	The ID of the asset rate card entry.
