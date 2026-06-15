---
article_id: ind.dro_context_definitions_for_dynamic_revenue_orchestrator.htm
title: Context Definitions for Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_context_definitions_for_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Context Definitions for Dynamic Revenue Orchestrator

Dynamic Revenue Orchestrator (DRO) context definitions contain the information required to fulfill a sales transaction. A context definition includes the relationship between nodes and their structure, attributes, context tags, and mapping. Context mapping updates the nodes and attributes with the correct input data from Salesforce objects.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Salesforce Dynamic Revenue Orchestrator is enabled.
Predefined Context Definitions

DRO’s predefined context definitions include:

Sales Transaction Context Definition
Provides the details of a sales transaction such as order line items, relationships, and attributes to the Decomposition process.
Fulfillment Asset Context Definition
Provides the quantities and attributes of the fulfillment assets to the decomposition process to determine the actions on the fulfillment order line items.
Customize Context Definitions for DRO

These predefined context definitions provide a baseline of functionality for sales order decomposition and fulfillment. To customize or extend these context definitions, consult these Context Service learning resources:

Trailhead: Context Service Basics
Key Terms in Context Service
Considerations

When you map a source product tag to a target product tag and if that target product tag is mapped to a reference field in the context definition mapping, enrichment happens only if the outcome of the mapping is compatible with the reference field of the target product tag. We recommend that you avoid selecting such product tags for the target product in the Fields & Attribute Mapping tab.

In the event of an enrichment failure, the Decision Explainer Service (DES) captures the information in the log. See the Explainability Action Logs section on Submit Order Action and Action Logs.
