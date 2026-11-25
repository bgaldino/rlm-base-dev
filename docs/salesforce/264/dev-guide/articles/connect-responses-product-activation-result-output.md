---
page_id: connect-responses-product-activation-result-output
title: Product Activation Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-activation-result-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_product_activation_result_output.htm
fetched_at: 2026-11-25
---

# Product Activation Result

Output representation of the activation outcome for a single product, including any errors that occurred while activating the product or its associated usage records.

## JSON Example

```
{
  "productId": "01txx0000006i2hAAA",
  "errors": [
    {
      "productUsageResourceId": "0iUxx000000009",
      "usageResourceId": "0hUxx000000003",
      "message": "Usage Resource not found for product",
      "objectApiName": "ProductUsageResource",
      "fieldName": "UsageResourceId",
      "recordId": null,
      "recordName": null
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Usage Activation Error](./connect-responses-usage-activation-error-output.md)[] | List of errors that occurred while activating the product or its associated usage records. | Big, 67.0 | 67.0 |
| `productId` | String | ID of the Product2 record that this activation outcome describes. | Big, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-activation-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
