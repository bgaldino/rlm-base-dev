---
page_id: connect_responses_error_output.htm
title: Error Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Error Details

Output representation of the top-level error detail when validation fails.

JSON example
:   This example shows a sample error
    response.

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
                "validationErrors": [],
                "validationWarnings": []
              }
            }
          ]
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Standardized error code. For example, `VALIDATION_FAILED`. | Big, 66.0 | 66.0 |
| `message` | String | Human-readable error message that describes the overall validation failure. | Big, 66.0 | 66.0 |
| `products` | [Product Validation Result](./connect_responses_product_validation_result_output.htm.md "Output representation of the validation result for a specific product.")[] | List of product validation results. | Big, 66.0 | 66.0 |
