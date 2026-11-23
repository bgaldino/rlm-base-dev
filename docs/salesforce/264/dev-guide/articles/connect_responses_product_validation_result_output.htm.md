---
page_id: connect_responses_product_validation_result_output.htm
title: Product Validation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_validation_result_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
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
| `productId` | String | Unique product ID that's being validated. | Big, 67.0 | 67.0 |
| `validationResult` | [Validation Result](./connect_responses_validation_result_output.htm.md "Output representation of the validation results grouped by rule name.") | Validation results grouped by rule name. | Big, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_validation_result_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
