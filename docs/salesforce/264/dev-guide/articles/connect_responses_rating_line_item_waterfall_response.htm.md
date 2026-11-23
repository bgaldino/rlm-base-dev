---
page_id: connect_responses_rating_line_item_waterfall_response.htm
title: Line Item Waterfall Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rating_line_item_waterfall_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Line Item Waterfall Response

Output representation of the line item waterfall response.

## JSON Example

```
{
       "currencyCode": "USD",
       "error": null,
       "executionEndTimestamp": "2023-07-31T20:11:29.625Z",
       "executionId": "gdLVwn2x1uats2xWMAjV",
       "executionStartTimestamp": null,
       "lineItemId": "item1",
       "success": true,
       "usageType":"Rating",
       "output": {
          "quantity": "10",
          "netUnitPrice": "10",
          "subtotal": "100"
        },
        "waterfall": []
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition​VersionId` | String | Context definition version ID of the rating procedure. | Small, 62.0 | 62.0 |
| `context​MappingId` | String | Context mapping ID of the record. | Small, 62.0 | 62.0 |
| `currency​Code` | String | Currency code. For example, USD or INR. | Small, 62.0 | 62.0 |
| `error` | [Rating Error Response](./connect_responses_rating_error_response.htm.md "Output representation of the error details related to the API request.") | Details of any errors. | Small, 62.0 | 62.0 |
| `execution​End​Timestamp` | String | End timestamp of procedure execution. | Small, 62.0 | 62.0 |
| `execution​Id` | String | Execution ID of a particular execution of a rating procedure. | Small, 62.0 | 62.0 |
| `execution​Start​Timestamp` | String | Start timestamp of procedure execution. | Small, 62.0 | 62.0 |
| `line​ItemId` | String | Line item ID for which the price is being calculated. | Small, 62.0 | 62.0 |
| `output` | Map<String, Object> | Output of the rating procedure. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `usage​Type` | String | Usage type of the waterfall log record. | Small, 62.0 | 62.0 |
| `waterfall` | [Rating Waterfall Response](./connect_responses_rating_waterfall_response.htm.md "Output representation of a rating waterfall request.")[] | Details of the rating waterfall. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rating_line_item_waterfall_response.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
