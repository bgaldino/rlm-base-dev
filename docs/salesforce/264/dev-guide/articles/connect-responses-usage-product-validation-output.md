---
page_id: connect-responses-usage-product-validation-output
title: Usage Product Validation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-product-validation-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_usage_product_validation_output.htm
fetched_at: 2026-11-25
---

# Usage Product Validation

Output representation of all the performed validations.

## JSON Example

This example shows the validation output with errors and warnings.

```
{
  "errors": [
    {
      "errorCode": "VALIDATION_FAILED",
      "message": "Product validation completed with cross-entity errors",
      "products": [
        {
          "productId": "01txx0000006i2gAAA",
          "validationResult": {
            "validationErrors": [
              {
                "errors": [
                  {
                    "errorCode": "EFFECTIVITY_MISMATCH",
                    "errorMessages": [
                      {
                        "errorMessage": "PUR and RCE effective date ranges must have overlap for proper rating functionality",
                        "errorDetails": [
                          {
                            "relatedObjectAPIName": "ProductUsageRule",
                            "records": [
                              {
                                "id": "a0bxx0000004CqZAAU",
                                "name": "PUR-001"
                              }
                            ]
                          }
                        ]
                      }
                    ]
                  }
                ],
                "ruleName": "Usage vs Rating Effectivity"
              }
            ],
            "validationWarnings": []
          }
        }
      ]
    }
  ],
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `success` | Boolean | Indicates whether the product validation passed (`true`) or failed (`false`). | Big, 66.0 | 66.0 |
| `errors` | [Error Details](./connect-responses-error-output.md)[] | List of top-level error details when validation fails. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-product-validation-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
