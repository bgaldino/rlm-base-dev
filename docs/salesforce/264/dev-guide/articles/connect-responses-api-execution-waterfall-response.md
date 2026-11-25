---
page_id: connect-responses-api-execution-waterfall-response
title: Pricing Execution Waterfall Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-execution-waterfall-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_api_execution_waterfall_response.htm
fetched_at: 2026-11-25
---

# Pricing Execution Waterfall Response

Output representation of the execution process that’s associated with a pricing waterfall.

## JSON Example

```
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
| `apiExecutionId` | String | Unique execution ID that’s generated each time a pricing API is executed. | Small, 63.0 | Small, 63.0 |
| `apiExecution​LogRepresentation​List` | [API Execution Log Response](./connect-responses-api-execution-log.md)[] | List of API execution logs. | Small, 63.0 | 63.0 |
| `currencyCode` | String | Currency code that’s stored in each API log record for the pricing execution. | Small, 67.0 | Small, 67.0 |
| `error` | [Pricing Error Response](./connect-responses-pricing-error-response.md) | Error details of the pricing execution process. | Small, 63.0 | Small, 63.0 |
| `executionId` | String | Unique ID that’s generated each time a pricing process is executed. | Small, 63.0 | Small, 63.0 |
| `id` | String | Unique record ID of the waterfall response. | Small, 65.0 | Small, 65.0 |
| `lineItemId` | String | Unique ID of the line item that’s associated with this pricing execution. | Small, 59.0 | Small, 59.0 |
| `referenceKey` | String | The reference ID that a consuming workstream provides in the API to search for the specific logs in the Pricing Operations Console. | Small, 63.0 | Small, 63.0 |
| `success` | Boolean | Indicates whether the API execution is successful (`true`) or not (`false`). | Small, 63.0 | Small, 63.0 |
| `usageType` | String | Usage type of the API execution. | Small, 63.0 | Small, 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-execution-waterfall-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
