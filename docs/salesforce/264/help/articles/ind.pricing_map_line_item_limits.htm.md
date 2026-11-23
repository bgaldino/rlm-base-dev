---
article_id: ind.pricing_map_line_item_limits.htm
title: Map Line Item Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_map_line_item_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_map_context_tags_in_pricing_procedures.htm
fetched_at: 2026-11-23
---

# Map Line Item Limits

Before you add the Map Line Item element to a pricing procedure, review these limitations and configuration requirements.

Use the Map Line Item element only for standard mapping. Adding custom logic or using the element primarily to persist values can degrade performance during pricing execution.
The Map Line Item element doesn't support parallel execution. To use this element, disable parallel execution for the pricing procedure.
Don't use the Map Line Item element together with delta pricing in the same use case.
The Map Line Item element doesn't support local list variables when Advanced Detail Line Pricing is turned on.
The Map Line Item element doesn't support derived pricing.
In both pricing and discovery procedures, place the Map Line Item element second in the procedure, immediately after the Pricing Setting element or the Discovery Settings element.
The Map Line Item element doesn't support the Date data type when Advanced Detail Line Pricing is turned on.
To map values to a quote line item detail, place the Map Line Item element second in the procedure, immediately after the Pricing Setting element. Use the Assignment element after the Map Line Item element to initialize the tags used in the Map Line Item element.
If you add custom fields to entities such as quote line items, quote line item details, order products, or order product details, update the context definition accordingly.
Map the custom field from the line item to the detail item. Don't write the value directly to the custom detail field. The element saves the value to the detail item when a detail item exists; otherwise, it saves the value to the line item.
For mapping limits for this element, see Salesforce Pricing Limits.
SEE ALSO
Advanced Detail Line Pricing Limits

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_map_line_item_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
