---
article_id: ind.rm_commitment_rate_adjustment.htm
title: Commitment Rate Adjustment
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_commitment_rate_adjustment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Commitment Rate Adjustment

The Commitment Rate Adjustment element applies rate adjustments and calculates rates for commitment-based products.

REQUIRED EDITIONS
Commitment Rate Adjustment Variables

Map the variables in the Commitment-based Rate Adjustment lookup table to the relevant context tags.

Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Input Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Asset Rate Card Entry: Asset ID	Asset	The ID of the asset record that's related to the sellable product that the usage resource is associated with.
Asset Rate Card Entry: Start Date	RatingDecisionDateTime	The start date of the transaction.
Asset Rate Card Entry: End Date	RatingDecisionDateTime	The end date of the transaction.
Output Rule Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Adjustment Type	Create a custom tag	Enter the adjustment type applicable to the usage resource.
Adjustment Value	Create a custom tag	Enter the adjustment value applicable to the usage resource.
Rate Card Entry: Usage Resource ID	Create a custom tag	The ID of the usage resource.
Rate Card Entry: Rate Unit of Measure Name	Create a custom tag	Enter the standard unit of measure related to the rate card entry.
Input Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Input Unit Rate	NetUnitRate	The total rate of the usage resource.
Output Usage Resource Field Name	Create a custom tag	The name of the usage resource.
Usage Resource	UsageResource	The ID of the usage resource.
Usage Category	UsageResourceCategory__std	The category of the usage resource.
Output Variables
PARAMETER NAME	MAPPED CONTEXT TAG	CONTEXT TAG’S DESCRIPTION
Net Unit Rate	CommitRate_std	The rate that's applicable to the usage resource consumed post the application of commitment discount.
