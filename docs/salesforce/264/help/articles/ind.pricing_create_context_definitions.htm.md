---
article_id: ind.pricing_create_context_definitions.htm
title: Context Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_context_definitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_get_ready_to_build_pricing_procedures.htm
fetched_at: 2026-09-07
---

# Context Definitions

Context definitions contain the necessary information to run the pricing process. This includes the relationship between nodes and their structure, attributes, context tags, and mapping. Mapping defines the nodes and attributes with the correct input data from Salesforce objects. The pricing procedure runs with its associated tags and writes the results back to the context definition that the tags belong to. A crucial point to remember is that a context tag can’t have the same name as the decision table's label or API name.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

End-to-end transactions in Revenue Management run on the SalesTransactionContext context definition. This context definition links sales transactions to objects such as quotes, assets, and orders.

IMPORTANT

Salesforce Pricing doesn't work directly with the SalesTransactionContext__stdctx base context definition. To use pricing procedures, always extend the base context. An extended context definition inherits the structure, nodes, and attributes from the base context definition while allowing you to add custom nodes, attributes, and tags for your pricing logic.
