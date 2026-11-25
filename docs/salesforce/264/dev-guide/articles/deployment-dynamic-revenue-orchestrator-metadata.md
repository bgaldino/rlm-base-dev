---
page_id: deployment-dynamic-revenue-orchestrator-metadata
title: Dynamic Revenue Orchestrator Metadata
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-dynamic-revenue-orchestrator-metadata.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-b
legacy_page_id: deployment_dynamic_revenue_orchestrator_metadata.htm
fetched_at: 2026-11-25
---

# Dynamic Revenue Orchestrator Metadata

This table provides the metadata deployment reference for Dynamic Revenue Orchestrator (DRO) in Revenue Management, including setup paths and configuration details.

| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Dynamic Revenue Orchestrator | Setup > Feature Settings > Dynamic Revenue Orchestrator |  |
| Flag | Dynamic Revenue Orchestrator | Setup > Feature Settings > Dynamic Revenue Orchestrator > Dynamic Revenue Orchestrator Settings |  |
| Flag | In-flight Amendments | Setup > Feature Settings > Dynamic Revenue Orchestrator > Dynamic Revenue Orchestrator Settings |  |
| Flag | Future Dated Steps | Setup > Feature Settings > Dynamic Revenue Orchestrator > Dynamic Revenue Orchestrator Settings |  |
| Flag | Link Task to Step Source | Setup > Feature Settings > Dynamic Revenue Orchestrator > Dynamic Revenue Orchestrator Settings |  |
| Field | Fulfillment User | Setup > Feature Settings > Dynamic Revenue Orchestrator > Dynamic Revenue Orchestrator Settings |  |
| Field | Context Definition | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Sales Transaction Header | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context field for Orchestration Group Key (Optional) | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Sales Transaction Item | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Sales Transaction Item Relationship | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Sales Transaction Item Attribute | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Fulfillment Transaction | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Fulfillment Transaction Item | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Fulfillment Transaction Item Relationship | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Fulfillment Transaction Item Attribute | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Node for Fulfillment Transaction Item Source Relationship | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Sales Transaction Context Definition) |  |
| Field | Context Definition | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Fulfillment Asset Context Definition) |  |
| Field | Context Node for Fulfillment Asset | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Fulfillment Asset Context Definition) |  |
| Field | Context Node for Fulfillment Asset Attribute | Setup > Feature Settings > Dynamic Revenue Orchestrator > Context Definition Settings (Fulfillment Asset Context Definition) |  |
| Flag | Fallout | Setup > Feature Settings > Dynamic Revenue Orchestrator > Fallout and SLA Settings |  |
| Flag | Service Level Agreement | Setup > Feature Settings > Dynamic Revenue Orchestrator > Fallout and SLA Settings |  |
| Permission Sets | DRO Admin User | Setup > Users > Permission Sets |  |
| Permission Sets | Submit Transactions and Fulfillment User | Setup > Users > Permission Sets |  |
| Permission Sets | Fulfillment Designer | Setup > Users > Permission Sets |  |
| Permission Sets | Fulfillment Manager/Operator | Setup > Users > Permission Sets |  |
| Setup | Procedure Plan Definition | Procedure Plan Setup > Procedure Plan Definitions | The value of `UsageType` field is `Dfo`. This is used to define an alternate context mapping for sales transaction context in an order submission flow. See [Submit Orders for Decomposition and Order Fulfillment](https://help.salesforce.com/s/articleView?id=ind.dro_run_time_administration.htm) |
| User Permission | Submit Transactions and Orchestrate User |  | Enables user to submit and orchestrate transactions for any object by using Dynamic Revenue Orchestrator. |

**See Also**

- [*Revenue Cloud Developer Guide*: DynamicFulfillmentOrchestratorSettings](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_dynamicfulfillmentorchestratorsettings.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-dynamic-revenue-orchestrator-metadata.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
