---
page_id: connect_responses_product_validation_result_output.htm
title: Product Validation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_validation_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Product Validation Result

Output representation of the validation result for a specific product.

JSON example
:   This example shows the product validation result.

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
