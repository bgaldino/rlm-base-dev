---
page_id: connect_responses_usage_product_validation_output.htm
title: Usage Product Validation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_product_validation_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Usage Product Validation

Output representation of all the performed validations.

JSON example
:   This example shows the validation output with errors and
    warnings.

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
| `errors` | [Error Details](./connect_responses_error_output.htm.md "Output representation of the top-level error detail when validation fails.")[] | List of top-level error details when validation fails. | Big, 66.0 | 66.0 |
