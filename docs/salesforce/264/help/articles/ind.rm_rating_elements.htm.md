---
article_id: ind.rm_rating_elements.htm
title: Explore Available Rating Elements in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rating_elements.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_procedures.htm
fetched_at: 2026-09-07
---

# Explore Available Rating Elements in Revenue Management

Rating elements are the building blocks of a rating procedure. A new rating procedure is always blank, and each added element forms a step in the rating procedure. Use the available rating elements to form logical steps in the rating procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Rating Setting
Use the Rating Setting element to map commonly used variables in a rating procedure to context tags.
Base Rate
To calculate the base rate of a usage resource based on the rate card type, use the Base Rate element.
Volume-Based Rate Discount
The Volume-Based Rate Discount element calculates the usage resource rate based on the discounts configured for the quantities consumed.
Tier-Based Rate Discount
The Tier-Based Rate Discount element determines the discount for a usage resource based on the quantity consumed.
Negotiated Rate Card Entries
Use the Negotiated Rate Card Entries element to determine the Rate Card Entry ID from the Asset ID.
Negotiated Rate Card Entries for Binding Object
Use the Negotiated Rate Card Entries element to determine the Rate Card Entry ID from the Binding Object Rate Card Entry ID.
Negotiated Base Rate
To calculate the negotiated rates applied on the base rate of the usage resource, use the Negotiated Base Rate element. The negotiated base rate element uses the Asset Rate lookup table to determine if rates were negotiated. If rates weren't negotiated, the element uses base rates.
Negotiated Base Rate for Binding Object
Use the Negotiated Base Rate element to calculate the negotiated target-specific rates. The negotiated base rate element uses the Binding Object Rate lookup table to determine if rates were negotiated. If rates weren't negotiated, the element uses base rates.
Negotiated Tier-Based Rate Adjustment
The Negotiated Tier-Based Rate Adjustment element calculates the negotiated rate for a usage resource based on the defined tiers, applying either a discount or a surcharge.
Negotiated Tier-Based Rate Adjustment for Binding Object
Use the Negotiated Tier-Based Rate Adjustment element to fetch the tier-based rate adjustment with bound range related to the binding object ID specified in the decision table along with other input values.
Negotiated Volume-Based Rate Adjustment
Ensure consistent surcharges or discounting across all relevant usage with the Negotiated Volume-Based Rate Adjustment element. The Negotiated Volume-Based Rate Adjustment element is similar to the Negotiated Tier-Based Rate Adjustment element. However, in volume-based rate adjustment, negotiated rates are applied uniformly to all quantities of the usage resource so that it's easier to uniformly manage volume-based negotiations.
Negotiated Volume-Based Rate Adjustment for Binding Object
Use the Negotiated Volume-Based Rate Adjustment element to fetch the volume-based rate adjustment related to the binding object ID specified in the decision table along with other input values.
Commitment Rate Adjustment
The Commitment Rate Adjustment element applies rate adjustments and calculates rates for commitment-based products.
Map Line Item
Use the Map Line Item element for precise mapping of variables. This element maps variables at the level of the main line item and the level of the sub-line items, which are created when multiple transactions occur on the same line item.
Manual Rate Discount
The Manual Rate Discount element calculates the final price of a product after you manually enter the external discounts.
Rate Adjustment Matrix
The Rate Adjustment Matrix element calculates the rate of a usage resource based on the discounts configured for a set of custom conditions.
Assignment
Use the Assignment element to set and change the context tag values of variables.
Formula-Based Rating
The Formula-Based Rating element performs functions and mathematical calculations to generate the rate of a usage resource.
List Group and List Operation
A list group element filters items in a list based on the filter conditions and then performs further operations on the filtered lists. A list operation is always the first step in the list group and defines how items in the list are filtered.
Rounding Values
The Rounding Values element assists in precisely calculating the rate of a usage resource by using rounding rules.
Stop Rating
Use the Stop Rating element to stop the execution of the rating procedure for a particular line item. During simulation, the Waterfall view shows the element that the rating procedure stopped at.
Get Rate Cards
Use the Get Rate Cards element to fetch the rate cards that you need for your rating procedure.
