---
page_id: connect_resources_pricing_process_execution.htm
title: Pricing Process Execution (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_pricing_process_execution.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Pricing Process Execution (GET)

Get the execution details of a pricing process by using the
execution ID.

Resource
:   ```
    /connect/core-pricing/pricing-process-execution/executionId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/core-pricing/pricing-process-execution/29646938297972
    ```

Available version
:   63.0

HTTP methods
:   GET

Path parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `executionId` | String | ID of the pricing process execution record. The ID is generated each time a pricing process is executed. | Required | 63.0 |

Query parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `executionType` | String | Type of execution that's defined internally within the pricing API. Valid values are:   - `API_Execution` - `Discovery`—Discovery   procedure - `Discovery_Line`—Discovery   procedure for the line items. - `Pricing`—Pricing   procedure - `Pricing_Line`—Pricing   procedure for the line items.   If the `executionType` parameter isn't specified, the API retrieves records for all the execution types that are associated with the specified execution ID. | Optional | 63.0 |

Response body for GET
:   [Pricing Process
    Execution Response](./connect_responses_pricing_process_execution_get_output.htm.md "Output representation of the details of a pricing process execution.")
