---
article_id: ind.pricing_discount_distribution_service_limits.htm
title: Discount Distribution Service Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_discount_distribution_service_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_discount_spread_service.htm
fetched_at: 2026-11-23
---

# Discount Distribution Service Limits

Before adding the Discount Distribution Service element to your pricing procedure, keep these points in mind:

You can't apply discount distribution to a pricing procedure that was used to calculate a product's derived price.
While Proration and Subscription elements update the LineItemSubTotal variable by multiplying the ProrationMultiplier with the NetUnitPrice tag, the Discount Distribution Service only utilizes the NetUnitPrice variable for its pricing calculations. If you intend to use the total subscription price, use a Formula element and provide the formula -Proration Multiplier * NetUnitPrice. Then, use the output of this formula as the InputPrice variable for calculations within the Discount Distribution Service element.
The Discount Distribution Service element must be the last element in the pricing procedure. Only a rounding element that handles currency decimal precision can follow it.
Use the Discount Distribution Service element only once per pricing procedure.
Include a Discount Distribution Service element in only one pricing procedure within a procedure plan.
Place the pricing procedure that contains the Discount Distribution Service element last in your procedure plan. Adding procedures after it can cause pricing calculation errors.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_discount_distribution_service_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
