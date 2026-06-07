---
article_id: ind.pricing_create_context_definitions.htm
title: Context Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_context_definitions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Context Definitions

Context definitions contain the necessary information to run the pricing process. This includes the relationship between nodes and their structure, attributes, context tags, and mapping. Mapping defines the nodes and attributes with the correct input data from Salesforce objects. The pricing procedure runs with its associated tags and writes the results back to the context definition that the tags belong to. A crucial point to remember is that a context tag can’t have the same name as the decision table's label or API name.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

Salesforce Pricing in Agentforce Revenue Management uses the SalesTransactionContext, a context definition that links sales transactions to objects such as quotes, assets, and orders. This can be extended to meet your business's specific pricing requirements.
