---
page_id: connect-responses-product-validation-result-output
title: Product Validation Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-validation-result-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_product_validation_result_output.htm
fetched_at: 2026-11-25
---

# Product Validation Result

Output representation of the validation result for a specific product.

## JSON Example

This example shows the product validation result.

```
{
  "products": [
    {
      "productId": "01txx0000006i2gAAA",
      "validationResult": {
        "validationErrors": [],
        "validationWarnings": []
      }
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `productId` | String | Unique product ID that’s being validated. | Big, 67.0 | 67.0 |
| `validationResult` | [Validation Result](./connect-responses-validation-result-output.md) | Validation results grouped by rule name. | Big, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-validation-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
