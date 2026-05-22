---
article_id: ind.rm_rating_discovery_procedures.htm
title: Rating Discovery Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rating_discovery_procedures.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Rating Discovery Procedures

Rating discovery procedures fetch the binding objects, rate cards, rate card entries, and rate adjustments associated with multiple sellable products and usage resources related to a price book. Use the retrieved rate information to provide quotes for usage-based products to customers by using Quote and Order Capture and Asset Lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Rating discovery procedure uses the predefined context definition called RatingDiscoveryContext that is used to map the Rate Management objects, such as Rate Card, Rate Card Entries, and Rate Adjustment by Tier. However, if you want to customize parts of this context definition for reuse, extend or clone it and make modifications. See Context Definitions.

Use these lookup tables for the rating discovery procedure:

Binding Object Rate Adjustment Resolution Entries
Binding Object Rate Card Entry Resolution Entries
Pricebook Rate Card Entries
Rate Card Entry Resolution Entries 2
Rate Adjustment by Tier Resolution Entries
Rate Adjustment by Attribute Resolution Entries
Clone the Default Rating Discovery Procedure
Clone the predefined rating discovery procedure available with Rate Management and customize it. You can also build a custom rating discovery procedure to meet your business’s unique needs.
Configure Your Rating Discovery Procedure
To retrieve rate cards, rate card entries, and related adjustments based on the filter criteria for the context input, use Rating discovery procedures.
/apex/HTViewHelpDoc?id=ind.Chunk1571878827.htm#rm_rating_discovery_procedure_elements
