---
article_id: ind.rm_rating_elements.htm
title: Explore Available Rating Elements in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rating_elements.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Explore Available Rating Elements in Agentforce Revenue Management

Rating elements are the building blocks of a rating procedure. A new rating procedure is always blank, and each added element forms a step in the rating procedure. Use the available rating elements to form logical steps in the rating procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Rating Setting
Use the Rating Setting element to map commonly used variables in a rating procedure to context tags.
Base Rate

Volume-Based Rate Discount

Tier-Based Rate Discount

Negotiated Rate Card Entries

Negotiated Rate Card Entries for Binding Object
Use the Negotiated Rate Card Entries element to determine the Rate Card Entry ID from the Binding Object Rate Card Entry ID.
Negotiated Base Rate

Negotiated Base Rate for Binding Object
Use the Negotiated Base Rate element to calculate the negotiated target-specific rates. The negotiated base rate element uses the Binding Object Rate lookup table to determine if rates were negotiated. If rates weren't negotiated, the element uses base rates.
Negotiated Tier-Based Rate Adjustment

Negotiated Tier-Based Rate Adjustment for Binding Object
Use the Negotiated Tier-Based Rate Adjustment element to fetch the tier-based rate adjustment with bound range related to the binding object ID specified in the decision table along with other input values.
Negotiated Volume-Based Rate Adjustment

Negotiated Volume-Based Rate Adjustment for Binding Object
Use the Negotiated Volume-Based Rate Adjustment element to fetch the volume-based rate adjustment related to the binding object ID specified in the decision table along with other input values.
Commitment Rate Adjustment
The Commitment Rate Adjustment element applies rate adjustments and calculates rates for commitment-based products.
Map Line Item
Use the Map Line Item element for precise mapping of variables. This element maps variables at the level of the main line item and the level of the sub-line items, which are created when multiple transactions occur on the same line item.
Manual Rate Discount

Rate Adjustment Matrix

Assignment
Use the Assignment element to set and change the context tag values of variables.
Formula-Based Rating
The Formula-Based Rating element performs functions and mathematical calculations to generate the rate of a usage resource.
List Group and List Operation
A list group element filters items in a list based on the filter conditions and then performs further operations on the filtered lists. A list operation is always the first step in the list group and defines how items in the list are filtered.
Rounding Values

Stop Rating
Use the Stop Rating element to stop the execution of the rating procedure for a particular line item. During simulation, the Waterfall view shows the element that the rating procedure stopped at.
Get Rate Cards
