---
article_id: ind.pricing_get_ready_to_create_pricing_actions.htm
title: Get Ready to Create Pricing Actions
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_get_ready_to_create_pricing_actions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_action_parameters.htm
fetched_at: 2026-11-23
---

# Get Ready to Create Pricing Actions

Before you create pricing actions, complete these prerequisites.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
Create Context Definitions with Mapping

Context definitions contain the information required to execute the pricing process. A context definition includes the relationship between nodes and their structure, attributes, context tags, and mapping. Mapping ensures that the nodes and attributes are updated with the right input data from the Salesforce objects. See Context Definitions and Map Context Definitions.

Create Pricing Procedures

Build pricing procedures by using pricing elements where each element forms a step in a pricing procedure. When a pricing procedure is executed with the associated context tags, the results of the pricing procedures are written back to the context definition that the tags belong to. See Build Your Pricing Procedures .

Configure Pricing Parameters for Standard Objects
To ensure that the standard pricing action button functions properly, define pricing parameters that connect it to a context definition, the context's mapping, and the pricing procedure for calculating product prices.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_get_ready_to_create_pricing_actions.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
