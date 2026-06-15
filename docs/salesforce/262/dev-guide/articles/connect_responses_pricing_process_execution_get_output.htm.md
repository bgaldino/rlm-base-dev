---
page_id: connect_responses_pricing_process_execution_get_output.htm
title: Pricing Process Execution Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_process_execution_get_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Process Execution Response

Output representation of the details of a pricing process execution.

JSON example
:   ```
     {
      "error": {},
      "isSuccess": true,
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
          "status": "Partial_Success"
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
          "status": "Partial_Success"
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
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Error encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates whether the response was generated successfully (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `pricingProcess​ExecutionList` | [Pricing Process Execution List](./connect_responses_pricing_process_execution_output.htm.md "Output representation of the execution details for different types of the pricing processes.") [] | List of the execution details of the pricing process. | Small, 63.0 | 63.0 |
