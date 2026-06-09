---
page_id: connect_responses_process_execution_line_item_details_get_output.htm
title: Pricing Process Execution Details for Line Items
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_get_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Process Execution Details for Line Items

Output representation of the pricing process execution details for the line items along
with the error details and response generation status.

JSON example
:   ```
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
