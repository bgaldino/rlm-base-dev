---
page_id: pricing_business_apis.htm
title: Salesforce Pricing Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pricing_business_apis.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_overview.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Business APIs

Perform pricing request, create context instance, sync pricing data, and manage pricing
recipes and pricing waterfall details by using Salesforce Pricing Business APIs.

This table lists the available Salesforce Pricing resources.

| Resource | Description |
| --- | --- |
| [`/connect/core-pricing/price-contexts/contextid`](./connect_resources_price_context.htm.md "Perform a pricing request by using the instance ID of a context.") (POST) | Perform a pricing request by using the instance ID of a context. |
| [`/connect/core-pricing/pricing`](./connect_resources_headless.htm.md "Create and hydrate context instance in a single request. Provide a comprehensive response that contains final pricing details per line items and related errors, if any.") (POST) | Create and hydrate context instance in a single request. Provide a comprehensive response that contains final pricing details per line items and related errors, if any. |
| [`/connect/core-pricing/sync/pricingSyncOrigin`](./connect_resources_pricing_data_sync.htm.md "Sync pricing data to ensure that the lookup tables contain the latest pricing data.") (GET) | Sync pricing data to ensure that the lookup tables contain the latest pricing data. |
| [`/connect/core-pricing/recipe`](./connect_resources_pricing_recipe.htm.md "Get the mapping details of pricing recipes to the associated pricing recipe table.") (GET) | Get the mapping details of pricing recipes to the associated pricing recipe table. |
| [`/connect/core-pricing/recipe/mapping`](./connect_resources_price_recipe_mapping.htm.md "Create a mapping between the pricing recipe and the Decision Tables. Post recipes with lookup tables or procedures.") (POST) | Create a mapping between the pricing recipe and the Decision Tables. Post recipes with lookup tables or procedures. |
| [`/connect/core-pricing/versioned-revise-details`](./connect_resources_versioned_revise_details.htm.md "Create revisions of a pricing request with versions for adjustment entities.") (POST) | Create revisions of a pricing request with versions for adjustment entities. |
| [`/connect/core-pricing/waterfall/lineItemId/executionId`](./connect_resources_pricing_waterfall_fetch.htm.md "Get the persisted price waterfall that stores the process logs. Price waterfall provides insights into every step of the pricing process.") (GET) | Get the persisted price waterfall that stores the process logs. Price waterfall provides insights into every step of the pricing process. |
| [`/connect/core-pricing/waterfall`](./connect_resources_pricing_waterfall_post.htm.md "Create a log of price waterfall. Price waterfall provides insights into every step of the pricing process.") (POST) | Create a log of price waterfall. Price waterfall provides insights into every step of the pricing process. |
| [`/connect/core-pricing/pbeDerivedPricingSourceProduct`](./connect_resources_pbe_source_pricing_derived_product.htm.md "Get the source product for the Price Book Entry (PBE) derived pricing.") (POST) | Get the source product for the Price Book Entry (PBE) derived pricing. |
| [/connect/core-pricing/apiexecutionlogs/executionId](./connect_resources_execution_logs.htm.md "Get the log details of a pricing API execution record by using the execution ID.") (GET) | Get the log details of a pricing API execution record by using the execution ID. |
| [/connect/core-pricing/pricing-process-execution/executionId](./connect_resources_pricing_process_execution.htm.md "Get the execution details of a pricing process by using the execution ID.") (GET) | Get the execution details of a pricing process by using the execution ID. |
| [/connect/core-pricing/pricing-process-execution/lineitems/executionId/executionType](./connect_resources_process_execution_line_item_details.htm.md "Get the pricing execution details for the line items of a pricing process by using the execution ID and execution type.") (GET) | Get the pricing execution details for the line items of a pricing process by using the execution ID and execution type. |
| [/connect/core-pricing/simulationInputVariablesWithData](./connect_resources_get_pricing_simulation_data_with_variables.htm.md "Get details of the pricing simulation input variables along with associated data.") (GET) | Get details of the pricing simulation input variables along with associated data. |

This section lists the available Procedure Plan Definition-related resources. Use
procedure plan definitions to define criteria for all pricing process-related requirements in
one central location, and to set up the procedures based on these requirements.

| Resource | Description |
| --- | --- |
| [`/connect/procedure-plan-definitions`](./connect_resources_get_procedure_plan_definition_records.htm.md "Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition.") (GET, POST) | Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition. |
| [`/connect/procedure-plan-definitions/procedurePlanDefinitionId`](./connect_resources_get_procedure_plan_definition_by_ID.htm.md "Get, update, or delete a procedure plan definition record by using the record ID.") (GET, PATCH, DELETE) | Get, update, or delete a procedure plan definition record by using the record ID. |
| [`/connect/procedure-plan-definitions/evaluate`](./connect_resources_evaluate_procedure_plan_definition_by_object.htm.md "Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details.") (POST) | Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details. |
| [`/connect/procedure-plan-definitions/evaluate/procedurePlanDefinitionName`](./connect_resources_evaluate_procedure_plan_by_definition_name.htm.md "Evaluate a procedure plan definition based on the name of a definition to check for prerequisites such as usage type and context mapping details.") (POST) | Evaluate a procedure plan definition based on the name of a definition to check for prerequisites such as usage type and context mapping details. |
| [`/connect/procedure-plan-definitions/procedurePlanDefinitionId/version`](./connect_resources_create_procedure_plan_version_record.htm.md "Create records of a procedure plan version with details.") (POST) | Create records of a procedure plan version with details. |
| [`/connect/procedure-plan-definitions/versions/procedurePlanVersionId`](./connect_resources_get_procedure_plan_version_details.htm.md "Get, update, or delete a procedure plan definition version record by using the record ID.") (GET, PATCH, DELETE) | Get, update, or delete a procedure plan definition version record by using the record ID. |

- **[Resources](./pricing_business_apis_rest_references.htm.md)**  
  Learn more about the available Salesforce Pricing resources.
- **[Request Bodies](./pricing_api_requests.htm.md)**  
  Learn more about the available Salesforce Pricing API request bodies.
- **[Response Bodies](./pricing_api_responses.htm.md)**  
  Learn more about the available Salesforce Pricing API response bodies.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "Connect REST API Developer Guide: Introduction - HTML (New Window)")
