---
page_id: connect_responses_pricing_process_execution_output.htm
title: Pricing Process Execution List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_process_execution_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Process Execution List

Output representation of the execution details for different types of the pricing
processes.

JSON example
:   ```
     {
      "pricingProcessExecutionList": [
        {
          "executionId": "12345",
          "executionType": "Pricing_Line",
          "executionTypeId": "111_LineItem1",
          "message": "The Pricing API execution was successful.",
          "status": "Success"
        },
        {
          "executionId": "12345",
          "executionType": "Api_Execution",
          "executionTypeId": "333",
          "status": "Success"
        },
        {
          "executionId": "12345",
          "executionType": "Discovery",
          "executionTypeId": "222",
          "status": "Success"
        },
        {
          "executionId": "12345",
          "executionType": "Pricing",
          "executionTypeId": "111",
          "status": "Failure"
        },
        {
          "executionId": "12345",
          "executionType": "Discovery_Line",
          "executionTypeId": "222_LineItem1",
          "status": "Success"
        },
        {
          "executionId": "12345",
          "executionType": "Pricing_Line",
          "executionTypeId": "111_LineItem2",
          "status": "Failure"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | Unique ID that's generated each time a pricing process is executed. | Small, 63.0 | 63.0 |
| `executionType` | String | Type of the execution that's defined internally within the pricing API. | Small, 63.0 | 63.0 |
| `executionTypeId` | String | Unique execution type ID that's generated internally for process executions, such as pricing or discovery procedures. | Small, 63.0 | 63.0 |
| `message` | String | Message that's generated when a pricing process is executed. | Small, 63.0 | 63.0 |
| `status` | String | Execution process status for a line item. Valid values are:  - `Failure` - `Partial_Success`—Applies to `Pricing` and `Discovery` procedures when execution for some line items fails. - `Success` | Small, 63.0 | 63.0 |
