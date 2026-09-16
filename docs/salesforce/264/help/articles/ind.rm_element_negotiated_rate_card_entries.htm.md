---
article_id: ind.rm_element_negotiated_rate_card_entries.htm
title: Negotiated Rate Card Entries
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiated_rate_card_entries.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Negotiated Rate Card Entries

Use the Negotiated Rate Card Entries element to determine the Rate Card Entry ID from the Asset ID.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Rate Card Entries Variables

Map the variables in the Asset Rate Card Entry 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Formula	Asset	The ID of the asset record that's related to the sellable product that the usage resource is associated with.
Usage Resource ID	UsageResource	The ID of the usage resource that's negotiated.
Unit of Measure ID	NetUnitRateUom	The ID of the standard unit of measure related to the rate card.
Start Date	RatingDecisionDateTime	The start date of the transaction.
End Date	RatingDecisionDateTime	The end date of the transaction.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Order	Create a custom tag	The order that determines the applicable binding object rate when multiple rates are defined for an Anchor target within an effective period.
Asset Rate Card Entry ID	Create a custom tag	The Asset Rate Card Entry ID associated with the Asset ID.
Rate Card Entry ID	Create a custom tag	The Rate Card Entry ID associated with the Asset ID.
Rate Card Entry: Rate Card Type	Create a custom tag	Specify if the rate card type is Attribute, Base, or Tier.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Tier Rate Card Entry ID	TierRateCardEntry	The ID of the Rate Card Entry of type Tier.
Base Rate Card Entry ID	BaseRateCardEntry	The ID of the Rate Card Entry of type Tier.
Binding Object Base Rate Card Entry	BindingObjectBaseRateCardEntry__std	The Binding Object Rate Card Entry of type Base.
Binding Object Tier Rate Card Entry	BindingObjectTierRateCardEntry__std	The Binding Object Rate Card Entry of type Tier.
Add the Negotiated Rate Card Entries Element
Here’s how you can add the Negotiated Rate Card Entries element to your rating procedure.
