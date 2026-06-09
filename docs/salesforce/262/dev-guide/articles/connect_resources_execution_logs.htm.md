---
page_id: connect_resources_execution_logs.htm
title: API Execution Logs (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_execution_logs.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# API Execution Logs (GET)

Get the log details of a pricing API execution record by using the
execution ID.

Resource
:   ```
    /connect/core-pricing/apiexecutionlogs/executionId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/core-pricing/apiexecutionlogs/29646938297972
    ```

Available version
:   63.0

HTTP methods
:   GET

Path parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `executionId` | String | ID of the pricing process execution record. | Required | 63.0 |

Response body for GET
:   [Pricing Execution
    Waterfall Response](./connect_responses_api_execution_waterfall_response.htm.md "Output representation of the execution process that's associated with a pricing waterfall.")
