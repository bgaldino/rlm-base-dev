---
article_id: ind.rm_rating_discovery_procedure_elements.htm
title: Elements in a Rating Discovery Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rating_discovery_procedure_elements.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_discovery_procedures.htm
fetched_at: 2026-09-07
---

# Elements in a Rating Discovery Procedure

Use Rating Discovery Procedure to get rates for your usage resource based on the specified Binding Object ID or Pricebook ID.

REQUIRED EDITIONS

Here’s a list of the variables and the associated context tags of the Rating Discovery Procedure elements used to create a rating discovery procedure.

Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
NOTE If you use all the elements in a rating discovery procedure and provide the value of the output for an element in simulation, then that element isn’t considered for fetching the results. For example, you use the Get Rate Cards, Get Rate Card Entries, and Get Tier-Based Rate Adjustments elements in a sequence. If you provide a valid Pricebook ID and Rate Card ID record when you simulate the procedure, Rating Discovery Procedure skips the Get Rate Cards element from the procedure and fetches the rate card entries and rate adjustments related to the provided rate card record.
Get Binding Object Rate Adjustment
To retrieve the binding object rate adjustment ID(s) and map the variables to the relevant context tags, use the Binding Object Rate Adjustment Resolution Entries lookup table.
Get Binding Object Rate Card Entries
To retrieve the binding object rate card entry IDs and map the variables to the relevant context tags, use the Binding Object Rate Card Entry Resolution Entries 2 lookup table.
Get Rate Cards
Select the Pricebook Rate Card Entries lookup table to fetch the rate card and map the variables to the relevant context tags.
Get Rate Card Entries
Select the Rate Card Entry Resolution Entries 2 lookup table to fetch the rate card entries related to the rate card fetched by using the Get Rate Card element. Then, map the variables to the relevant context tags.
Get Tier-Based Rate Adjustments
Select the Rate Adjustment by Tier Resolution Entries lookup table to fetch the tier-based adjustments, and then map the variables to the relevant context tags.
