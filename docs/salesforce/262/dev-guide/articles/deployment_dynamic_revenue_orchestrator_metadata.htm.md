---
page_id: deployment_dynamic_revenue_orchestrator_metadata.htm
title: Dynamic Revenue Orchestrator Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_dynamic_revenue_orchestrator_metadata.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-06-09
---

# Dynamic Revenue Orchestrator Metadata

This table provides the metadata deployment reference for Dynamic Revenue Orchestrator
(DRO) in Revenue Cloud, including setup paths and configuration details.

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
| Setup | Procedure Plan Definition | Procedure Plan Setup > Procedure Plan Definitions | The value of UsageType field is `Dfo`. This is used to define an alternate context mapping for sales transaction context in an order submission flow. See [Submit Orders for Decomposition and Order Fulfillment](https://help.salesforce.com/s/articleView?id=ind.dro_run_time_administration.htm&language=en_US) |
| User Permission | Submit Transactions and Orchestrate User |  | Enables user to submit and orchestrate transactions for any object by using Dynamic Revenue Orchestrator. |

#### See Also

- [*Revenue Cloud Developer Guide*:
  DynamicFulfillmentOrchestratorSettings](./meta_dynamicfulfillmentorchestratorsettings.htm.md "Revenue Cloud Developer Guide:
         DynamicFulfillmentOrchestratorSettings - HTML (New Window)")
