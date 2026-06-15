---
page_id: connect_requests_delete_ramp_deal_input.htm
title: Delete Ramp Deal Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_delete_ramp_deal_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Delete Ramp Deal Input

Input representation of the request to delete a ramp deal.

JSON example
:   ```
    {
      "rampDealIds": [
        "0Q0xx0000004CDxCAM",
        "0QLxx0000004CSOGA2"
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `rampDeal​Ids` | String[] | Ramp identifier on the quote line item or order item. | Required | 62.0 |
