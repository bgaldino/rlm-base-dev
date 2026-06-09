---
page_id: connect_responses_api_execution_waterfall_response.htm
title: Pricing Execution Waterfall Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_api_execution_waterfall_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Execution Waterfall Response

Output representation of the execution process that's associated with a pricing
waterfall.

JSON example
:   ```
    {
      "apiEndpoint": "/connect/core-pricing/pricing",
      "apiExecutionId": "263369316770986",
      "apiExecutionLogRepresentationList": [
        {
          "message": [
            "The Pricing API couldn't be run. Try again, and if the issue persists, ask your admin for help."
          ]
        }
      ],
      "currencyCode": "USD",
      "executionId": "263369316895959",
      "id": "263369316895960",
      "lineItemId": null,
      "referenceKey": "referenceKey-ABCD",
      "success": false,
      "usageType": "Api_Execution"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `apiEndpoint` | String | API endpoint that ran during the pricing request. | Small, 63.0 | Small, 63.0 |
| `apiExecutionId` | String | Unique execution ID that's generated each time a pricing API is executed. | Small, 63.0 | Small, 63.0 |
| `apiExecution​LogRepresentation​List` | [API Execution Log Response](./connect_responses_api_execution_log.htm.md "Output representation of the execution log of a pricing waterfall request.")[] | List of API execution logs. | Small, 63.0 | 63.0 |
| `currencyCode` | String | Currency code that’s stored in each API log record for the pricing execution. | Small, 67.0 | Small, 67.0 |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Error details of the pricing execution process. | Small, 63.0 | Small, 63.0 |
| `executionId` | String | Unique ID that's generated each time a pricing process is executed. | Small, 63.0 | Small, 63.0 |
| `id` | String | Unique record ID of the waterfall response. | Small, 65.0 | Small, 65.0 |
| `lineItemId` | String | Unique ID of the line item that's associated with this pricing execution. | Small, 59.0 | Small, 59.0 |
| `referenceKey` | String | The reference ID that a consuming workstream provides in the API to search for the specific logs in the Pricing Operations Console. | Small, 63.0 | Small, 63.0 |
| `success` | Boolean | Indicates whether the API execution is successful (`true`) or not (`false`). | Small, 63.0 | Small, 63.0 |
| `usageType` | String | Usage type of the API execution. | Small, 63.0 | Small, 63.0 |
