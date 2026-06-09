---
page_id: connect_requests_sales_transaction_operand_input.htm
title: Sales Transaction Operand Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sales_transaction_operand_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Sales Transaction Operand Input

Input representation of a filter operand for reading sales transaction context
data.

JSON example
:   ```
    {
      "operands": [
        {
          "value": "Draft",
          "type": "STRING"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `value` | String | Operand value used by the filter condition. | Required | 67.0 |
    | `type` | String | Data type of the operand value. Valid values are:   - `STRING` - `NUMBER` - `BOOLEAN` - `DATETIME` - `DATE` | Required | 67.0 |
