---
page_id: connect_responses_process_execution_line_item_details_response.htm
title: Line Item Details Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_process_execution_line_item_details_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Line Item Details Response

Output representation of the pricing process execution details for the line
items.

JSON example
:   ```
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
| `status` | String | Specifies whether the pricing process execution for the line item is successful or has failed. Valid values are:  - `Success` - `Failure` | Small, 63.0 | 63.0 |
