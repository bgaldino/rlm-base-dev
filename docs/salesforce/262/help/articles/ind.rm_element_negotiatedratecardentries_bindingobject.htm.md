---
article_id: ind.rm_element_negotiatedratecardentries_bindingobject.htm
title: Negotiated Rate Card Entries for Binding Object
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_negotiatedratecardentries_bindingobject.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Negotiated Rate Card Entries for Binding Object

Use the Negotiated Rate Card Entries element to determine the Rate Card Entry ID from the Binding Object Rate Card Entry ID.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Negotiated Rate Card Entries Variables

Map the variables in the Binding Object Rate Card Entry 2 lookup table to the relevant context tags.

Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object ID	BindingObject__std	The ID of the binding object record that's related to the sellable product that the usage resource is associated with.
Usage Resource ID	UsageResource	The ID of the usage resource that's negotiated.
Unit of Measure ID	NetUnitRateUom	The ID of the standard unit of measure related to the rate card.
EffectiveFrom	RatingDecisionDateTime	The start date of the transaction.
EffectiveTo	RatingDecisionDateTime	The end date of the transaction.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Binding Object Rate Order	Create a custom tag	Determines the applicable binding object rate when multiple rates are defined for an Anchor target within an effective period.
Binding Object Rate Card Entry ID	Create a custom tag	The ID of the Binding Object Rate Card Entry.
Rate Card Entry ID	Create a custom tag	The Rate Card Entry ID associated with the Binding Object ID.
Rate Card Type	Create a custom tag	Specify if the rate card type is Attribute, Base, or Tier.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Tier Rate Card Entry ID	TierRateCardEntry	The ID of the Rate Card Entry of type Tier.
Base Rate Card Entry ID	BaseRateCardEntry	The ID of the Rate Card Entry of type Base.
 	 	 
Binding Object Base Rate Card Entry	BindingObjectBaseRateCardEntry__std	The ID of the Binding Object Rate Card Entry of type Base.
Binding Object Tier Rate Card Entry	BindingObjectTierRateCardEntry__std	The ID of the Binding Object Rate Card Entry of type Tier.
