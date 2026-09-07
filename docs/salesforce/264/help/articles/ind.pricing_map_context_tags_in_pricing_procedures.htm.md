---
article_id: ind.pricing_map_context_tags_in_pricing_procedures.htm
title: Map Context Tags
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_map_context_tags_in_pricing_procedures.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Map Context Tags

Simplify context tag mapping by using pricing elements to streamline variable mapping, ensuring accurate and straightforward pricing configurations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

Context tags connect pricing procedure variables to fields in your context definition. Without these mappings, the pricing procedure can't read input data from the transaction or write calculated values back to it.

IMPORTANT When price waterfall is enabled in your pricing settings, you must map the price_water_fall context tag in both the Pricing Setting and Map Line Item elements. If the Map Line Item element doesn't include this mapping, you receive the error: "Specify a context tag for the Price Waterfall variable in the Map Line Item element when price waterfall is enabled and setup in the Pricing Settings element."

Two pricing elements handle context tag mapping.

Pricing Setting
The Pricing Setting element serves as the initial element for any pricing procedure. They're used to map common variables in a pricing procedure to context tags.
Map Line Item
The Map Line Item element is used for precise mapping of variables. It maps variables at the main line item level and sub-line item levels, which are created when multiple transactions occur on the same line item within different pricing elements.
Map Line Item Limits
Before you add the Map Line Item element to a pricing procedure, review these limitations and configuration requirements.
