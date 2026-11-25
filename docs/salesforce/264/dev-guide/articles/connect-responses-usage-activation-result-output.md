---
page_id: connect-responses-usage-activation-result-output
title: Usage Activation Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-activation-result-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_usage_activation_result_output.htm
fetched_at: 2026-11-25
---

# Usage Activation Result

Output representation that groups the activation outcome and the validation outcome for the product in a usage product activation request.

## JSON Example

```
{
  "productActivationResults": [
    {
      "productId": "01txx0000006i2hAAA",
      "errors": []
    }
  ],
  "productValidationResults": [
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
| `product​ActivationResults` | [Product Activation Result](./connect-responses-product-activation-result-output.md)[] | List of product activation results. | Big, 67.0 | 67.0 |
| `product​ValidationResults` | [Product Validation Result](./connect-responses-product-validation-result-output.md)[] | List of product validation results. | Big, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-activation-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
