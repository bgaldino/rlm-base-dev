---
page_id: connect_resources_get_pricing_simulation_data_with_variables.htm
title: Pricing Simulation Input Variables With Data (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_pricing_simulation_data_with_variables.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Pricing Simulation Input Variables With Data (GET)

Get details of the pricing simulation input variables along with
associated data.

Resource
:   ```
    /connect/core-pricing/simulationInputVariablesWithData
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/core-pricing/simulationInputVariablesWithData?expressionSetVersionId=9QMxx0000004CDsGAM&entityId=0Q0xx0000004C92CAE&contextDefinitionId=SalesTransactionContext__stdctx&contextMappingId=QuoteEntitiesMapping
    ```

Available version
:   64.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `context​DefinitionId` | String | ID or developer name of the context definition. | Required | 64.0 |
    | `contextMapping​Id` | String | ID or name of the context mapping that's used. | Required | 64.0 |
    | `entityId` | String | ID of a quote or an order. | Required | 64.0 |
    | `expressionSet​VersionId` | String | ID of the expression set that starts with `9QM`. | Required | 64.0 |

Response body for GET
:   [Pricing Simulation
    Input Variables With Data](./connect_responses_pricing_simulation_input_variables_with_data_output.htm.md "Output representation of the pricing simulation variables with data.")
