---
page_id: pricing-business-apis
title: Salesforce Pricing Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-business-apis.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-overview
legacy_page_id: pricing_business_apis.htm
fetched_at: 2026-11-25
---

# Salesforce Pricing Business APIs

Perform pricing request, create context instance, sync pricing data, and manage pricing recipes and pricing waterfall details by using Salesforce Pricing Business APIs.

This table lists the available Salesforce Pricing resources.

| Resource | Description |
| --- | --- |
| [`/connect/core-pricing/price-contexts/{contextid}`](./connect-resources-price-context.md) (POST) | Perform a pricing request by using the instance ID of a context. |
| [`/connect/core-pricing/pricing`](./connect-resources-headless.md) (POST) | Create and hydrate context instance in a single request. Provide a comprehensive response that contains final pricing details per line items and related errors, if any. |
| [`/connect/core-pricing/sync/{pricingSyncOrigin}`](./connect-resources-pricing-data-sync.md) (GET) | Sync pricing data to ensure that the lookup tables contain the latest pricing data. |
| [`/connect/core-pricing/recipe`](./connect-resources-pricing-recipe.md) (GET) | Get the mapping details of pricing recipes to the associated pricing recipe table. |
| [`/connect/core-pricing/revenue/pricing-recipe/valid-elements`](./connect-resources-get-valid-pricing-elements.md) (GET) | Get the list of valid pricing element type API names for a given Pricing Usage Sub Type. |
| [`/connect/core-pricing/revenue/pricing-recipe/clone`](./connect-resources-clone-pricing-recipe.md) (POST) | Clone a pricing recipe with all its associated pricing recipe table mappings. |
| [`/connect/core-pricing/recipe/mapping`](./connect-resources-price-recipe-mapping.md) (POST) | Create a mapping between the pricing recipe and the Decision Tables. Post recipes with lookup tables or procedures. |
| [`/connect/core-pricing/versioned-revise-details`](./connect-resources-versioned-revise-details.md) (POST) | Create revisions of a pricing request with versions for adjustment entities. |
| [`/connect/core-pricing/waterfall/{lineItemId}/{executionId}`](./connect-resources-pricing-waterfall-fetch.md) (GET) | Get the persisted price waterfall that stores the process logs. Price waterfall provides insights into every step of the pricing process. |
| [`/connect/core-pricing/waterfall`](./connect-resources-pricing-waterfall-post.md) (POST) | Create a log of price waterfall. Price waterfall provides insights into every step of the pricing process. |
| [`/connect/core-pricing/pbeDerivedPricingSourceProduct`](./connect-resources-pbe-source-pricing-derived-product.md) (POST) | Get the source product for the Price Book Entry (PBE) derived pricing. |
| [/connect/core-pricing/apiexecutionlogs/*executionId*](./connect-resources-execution-logs.md) (GET) | Get the log details of a pricing API execution record by using the execution ID. |
| [/connect/core-pricing/pricing-process-execution/*executionId*](./connect-resources-pricing-process-execution.md) (GET) | Get the execution details of a pricing process by using the execution ID. |
| [/connect/core-pricing/pricing-process-execution/lineitems/*executionId*/*executionType*](./connect-resources-process-execution-line-item-details.md) (GET) | Get the pricing execution details for the line items of a pricing process by using the execution ID and execution type. |
| [/connect/core-pricing/simulationInputVariablesWithData](./connect-resources-get-pricing-simulation-data-with-variables.md) (GET) | Get details of the pricing simulation input variables along with associated data. |

This section lists the available Procedure Plan Definition-related resources. Use procedure plan definitions to define criteria for all pricing process-related requirements in one central location, and to set up the procedures based on these requirements.

| Resource | Description |
| --- | --- |
| [`/connect/procedure-plan-definitions`](./connect-resources-get-procedure-plan-definition-records.md) (GET, POST) | Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition. |
| [`/connect/procedure-plan-definitions/{procedurePlanDefinitionId}`](./connect-resources-get-procedure-plan-definition-by-id.md) (GET, PATCH, DELETE) | Get, update, or delete a procedure plan definition record by using the record ID. |
| [`/connect/procedure-plan-definitions/evaluate`](./connect-resources-evaluate-procedure-plan-definition-by-object.md) (POST) | Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details. |
| [`/connect/procedure-plan-definitions/evaluate/{procedurePlanDefinitionName}`](./connect-resources-evaluate-procedure-plan-by-definition-name.md) (POST) | Evaluate a procedure plan definition based on the name of a definition to check for prerequisites such as usage type and context mapping details. |
| [`/connect/procedure-plan-definitions/{procedurePlanDefinitionId}/version`](./connect-resources-create-procedure-plan-version-record.md) (POST) | Create records of a procedure plan version with details. |
| [`/connect/procedure-plan-definitions/versions/{procedurePlanVersionId}`](./connect-resources-get-procedure-plan-version-details.md) (GET, PATCH, DELETE) | Get, update, or delete a procedure plan definition version record by using the record ID. |

- 

**[Resources](./pricing-business-apis-rest-references.md)**

Learn more about the available Salesforce Pricing resources.

- 

**[Request Bodies](./pricing-api-requests.md)**

Learn more about the available Salesforce Pricing API request bodies.

- 

**[Response Bodies](./pricing-api-responses.md)**

Learn more about the available Salesforce Pricing API response bodies.

**See Also**

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-business-apis.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
