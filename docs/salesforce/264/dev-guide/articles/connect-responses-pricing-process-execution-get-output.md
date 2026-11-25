---
page_id: connect-responses-pricing-process-execution-get-output
title: Pricing Process Execution Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-process-execution-get-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_pricing_process_execution_get_output.htm
fetched_at: 2026-11-25
---

# Pricing Process Execution Response

Output representation of the details of a pricing process execution.

## JSON Example

```
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
| `error` | [Pricing Error Response](./connect-responses-pricing-error-response.md) | Error encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates whether the response was generated successfully (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `pricingProcess​ExecutionList` | [Pricing Process Execution List](./connect-responses-pricing-process-execution-output.md) [] | List of the execution details of the pricing process. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-process-execution-get-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
