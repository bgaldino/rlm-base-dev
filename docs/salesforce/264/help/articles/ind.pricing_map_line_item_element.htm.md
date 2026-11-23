---
article_id: ind.pricing_map_line_item_element.htm
title: Map Line Item
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_map_line_item_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_map_context_tags_in_pricing_procedures.htm
fetched_at: 2026-11-23
---

# Map Line Item

The Map Line Item element is used for precise mapping of variables. It maps variables at the main line item level and sub-line item levels, which are created when multiple transactions occur on the same line item within different pricing elements.

This element is valuable for mapping variables in both discovery and pricing processes. It must be placed second in line, immediately following either the Discovery Settings or Pricing Settings element.

Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
Click to add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Click to add the Map Line Item element to map your variables to the appropriate context tags at both the context node level and the child node level.
Map Line Item Limits
Before you add the Map Line Item element to a pricing procedure, review these limitations and configuration requirements.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_map_line_item_element.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
