---
page_id: connect_responses_usage_activation_output.htm
title: Usage Product Activation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_activation_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Usage Product Activation

Output representation of a usage product activation response.

JSON example
:   ```
    {
      "success": true,
      "errors": null,
      "activatedProducts": [
        "01txx0000006i2hAAB"
      ],
      "activationResults": {
        "productActivationResults": [
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
              },
              {
                "productUsageResourceId": "0iUxx0000000678",
                "usageResourceId": "0hUxx000000004",
                "message": "Related Unit of measure records is inactive, activate it first.",
                "objectApiName": "ProductUsageGrant",
                "fieldName": "DefaultUnitofMeasure",
                "recordId": "1BXSM000000404f4AA",
                "recordName": "PUG-000000001"
              }
            ]
          }
        ],
        "productValidationResults": [
          {
            "productId": "01txx0000006i2gAAA",
            "validationResult": {
              "validationErrors": [
                {
                  "ruleName": "Usage vs Rating Effectivity",
                  "errors": [
                    {
                      "errorCode": "EFFECTIVITY_MISMATCH",
                      "errorMessages": [
                        {
                          "errorMessage": "PUR and RCE effective date ranges must overlap for proper rating functionality.",
                          "errorDetails": [
                            {
                              "relatedObjectAPIName": "ProductUsageResource",
                              "records": [
                                {
                                  "id": "0Wnxx0000004CDEAA2",
                                  "name": "API Calls PUR"
                                }
                              ]
                            },
                            {
                              "relatedObjectAPIName": "RateCardEntry",
                              "records": [
                                {
                                  "id": "0Rcxx0000004FGHAA2",
                                  "name": "API Calls Rate Entry"
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ],
              "validationWarnings": []
            }
          }
        ]
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `activated​Products` | String[] | ID of the product whose associated usage records were activated. The array contains at most one entry. | Big, 67.0 | 67.0 |
| `activation​Results` | [Usage Activation Result](./connect_responses_usage_activation_result_output.htm.md "Output representation that groups the activation outcome and the validation outcome for the product in a usage product activation request.") | Activation and validation outcome for the product in the request. | Big, 67.0 | 67.0 |
| `errors` | [Generic Error](./connect_responses_generic_error_output.htm.md "Output representation of the error details encountered during the API request.")[] | List of top-level API errors. For example, a guardrail violation or an invalid request. | Big, 67.0 | 67.0 |
| `success` | Boolean | Indicates whether the API request was processed (`true`) or rejected at the top level (`false`). | Big, 67.0 | 67.0 |
