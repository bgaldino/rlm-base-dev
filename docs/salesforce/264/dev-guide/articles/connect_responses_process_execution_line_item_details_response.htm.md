---
page_id: connect_responses_process_execution_line_item_details_response.htm
title: Line Item Details Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-11-23
---

# Line Item Details Response

Output representation of the pricing process execution details for the line items.

## JSON Example

```
 {
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
| `lineItemId` | String | ID of the line item that the pricing process is executed for. | Small, 63.0 | 63.0 |
| `status` | String | Specifies whether the pricing process execution for the line item is successful or has failed. Valid values are `Success` or `Failure`. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_response.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
