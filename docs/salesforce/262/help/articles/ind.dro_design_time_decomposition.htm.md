---
article_id: ind.dro_design_time_decomposition.htm
title: Design Your Order Decomposition
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_design_time_decomposition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Design Your Order Decomposition

Define how your commercial products decompose into technical products that your order fulfillment team can deliver to your customers. Products decompose based on rules you define, and the technical products can inherit field and attribute data from related commerical products.

REQUIRED EDITIONS
Available in: Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
NOTE Dynamic Revenue Orchestrator relies on having a product catalog populated with both commercial and technical products. If you aren't familiar with building a product catalog, see Product Catalog Management.

When an order is submitted, the order line items decompose into fulfillment order line items. Your fulfillment designer creates the decomposition rules and mappings necessary to fulfill a commercial order with its technical products.

To get started designing your order decomposition solution, follow these instructions:

/apex/HTViewHelpDoc?id=ind.Chunk1935206448.htm#dro_technical_product_in_dro

Define Technical Product Attribute Scope
Use technical product attribute scopes to define the role of product attributes in decomposition and assetization. The scope determines whether attribute changes trigger fulfillment or supplemental actions on decomposed line items, or impact fulfillment assets. Defining these scopes at design time optimizes orchestration by processing only relevant updates and keeping asset data lean.
Define How a Product Decomposes
Use the decomposition workspace to set up rules that control how a commercial product or product classification breaks down into technical products. Define conditions and priorities for the decomposition rules. By default, all products decompose into fulfillment line items unless you specify an execution rule.
Define Execution Rules for a Decomposition Rule
To apply logic that determines when a specific decomposition rule runs, define execution rules that specify the conditions for the rule. By default, products decompose into fulfillment line items independent of execution rules.
Define Field and Attribute Mapping
Define how Dynamic Revenue Orchestrator (DRO) maps fields and attribute data between products. DRO uses this mapping to copy or transform commercial order data to the data that fulfillment systems or processes require.
Context Definitions for Dynamic Revenue Orchestrator
Dynamic Revenue Orchestrator (DRO) context definitions contain the information required to fulfill a sales transaction. A context definition includes the relationship between nodes and their structure, attributes, context tags, and mapping. Context mapping updates the nodes and attributes with the correct input data from Salesforce objects.
Decompose Ramp Deal Orders
Use Dynamic Revenue Orchestrator to decompose and fulfill ramp deals. A ramp deal is an order containing standalone line items that are divided into segments. Each segment can vary in price, quantity, and discount over different periods.
Unit Of Measure Inheritance and Rounding Values
During decomposition, the fulfillment order product inherits the unit of measure from the related technical product. During technical assetization, the fulfillment asset inherits the unit of measure from the corresponding fulfillment order line item.
SEE ALSO
Ramp Deals
