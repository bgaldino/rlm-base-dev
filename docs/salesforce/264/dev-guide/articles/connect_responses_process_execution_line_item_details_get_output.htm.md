---
page_id: connect_responses_process_execution_line_item_details_get_output.htm
title: Pricing Process Execution Details for Line Items
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_get_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-11-23
---

# Pricing Process Execution Details for Line Items

Output representation of the pricing process execution details for the line items along with the error details and response generation status.

## JSON Example

```
 {
  "error": {},
  "isSuccess": true,
  "lineItemDetailsList": [
    {
      "lineItemId": "LineItem1",
      "status": "Success"
    },
    {
      "lineItemId": "LineItem2",
      "status": "Success"
    },
    {
      "lineItemId": "LineItem3",
      "status": "Failure"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Error encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates whether the response was generated successfully (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `lineItemDetails​List` | [Line Item Details Response](./connect_responses_process_execution_line_item_details_response.htm.md "Output representation of the pricing process execution details for the line items.") [] | List of the line items for which the pricing process is executed. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_get_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
