---
article_id: ind.product_catalog_context_definitions_for_product_catalog_management.htm
title: Configure a Context Definition for Qualification Rules
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_context_definitions_for_product_catalog_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Configure a Context Definition for Qualification Rules

For qualification rules, context definitions pass product or product catagory data to your qualification rule procedures. The qualification procedure then evaluates the qualification of products or product categories and returns the qualification or disqualification results back to the context definition.

REQUIRED EDITIONS
View supported products and editions.

When building a qualification rule, you must map your evaluation criteria in the qualification context definition. However, before you can map the data, you must extend the built-in ProductDiscoveryContext context definition.

TIP

Before you extend the built-in context definition, check to see if there's an extended context definition you can use. Some organizations already have a customizable context definition called BrowseProductsCtxDefinition.

You can view your existing context definitions in Setup | Context Service | Context Definitions.

To configure a context definition for your qualification rules, follow these instructions:

Extend the ProductDiscoveryContext Context Definition
To add the nodes, attributes, mappings, and tags for your qualification procedure, extend the ProductDiscoveryContext context definition.
Nodes and Attributes in the ProductDiscoveryContext Context Definition
The ProductDiscoveryContext context definition contains nodes and attributes that are used by and populated by Product Discovery, pricing procedure, qualification procedure, and object mapping.
