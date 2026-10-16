---
article_id: ind.rm_element_get_rate_card_entries.htm
title: Get Rate Card Entries
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_get_rate_card_entries.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_discovery_procedure_elements.htm
fetched_at: 2026-09-07
---

# Get Rate Card Entries

Select the Rate Card Entry Resolution Entries 2 lookup table to fetch the rate card entries related to the rate card fetched by using the Get Rate Card element. Then, map the variables to the relevant context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Effective From	FilterEffectiveFrom	The date when the rate card entry becomes active.
Effective To	FilterEffectiveFrom	The date when the rate card entry becomes active.
Usage Resource	FilterUsageResource	The ID of the usage resource related to the rate card entry.
Product	FilterProduct	The ID of the sellable product.
Product Selling Model	FilterProductSellingModel__std	The method used to sell a product.
Rate Unit Of Measure	FilterRateUoM	The unit of measure of the rate defined for the usage resource.
Status	Predefined Constant	Specify whether the rate card entry is draft, active, or inactive.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Default Unit Of Measure	DefaultUnitOfMeasure	The default unit of measure applicable to the usage resource.
Rate Card Entry ID	RateCardEntryId	The ID of the rate card entry.
Rate	Rate	The rate defined for the rate card.
Rate Card Type	RCType	The type of rate card, such as attribute or tier.
Rate Unit Of Measure Name	RateUnitOfMeasureName	The unit of measure applicable for the rate defined in the rate card.
Usage Product	UsageProduct	The ID of the usage product that the rates are defined for.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card ID	RateCardId	The ID of the rate card.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Entry ID	RateCardEntryId	The ID of the rate card entry.
