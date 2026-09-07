---
article_id: ind.rm_rating_element_get_rate_cards.htm
title: Get Rate Cards
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rating_element_get_rate_cards.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-09-07
---

# Get Rate Cards

Use the Get Rate Cards element to fetch the rate cards that you need for your rating procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
NOTE Note: Use the existing Pricebook Rate Card Entries lookup table to create a new lookup table for the Get Rate Cards element. Use the get rate card element to fetch the rate card and map the variables to the relevant context tags.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card Type	RCType	The type of rate card, such as attribute or tier.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Price Book	PricebookId	The ID of the pricebook.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Rate Card ID	RateCardId	The ID of the rate card.
Add Get Rate Cards Element
Here’s how you can add the Get Rate Cards element to your rating procedure.
