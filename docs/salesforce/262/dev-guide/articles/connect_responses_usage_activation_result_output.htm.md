---
page_id: connect_responses_usage_activation_result_output.htm
title: Usage Activation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_activation_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Usage Activation Result

Output representation that groups the activation outcome and the validation outcome
for the product in a usage product activation request.

JSON example
:   ```
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
| `product​ActivationResults` | [Product Activation Result](./connect_responses_product_activation_result_output.htm.md "Output representation of the activation outcome for a single product, including any errors that occurred while activating the product or its associated usage records.")[] | List of product activation results. | Big, 67.0 | 67.0 |
| `product​ValidationResults` | [Product Validation Result](./connect_responses_product_validation_result_output.htm.md "Output representation of the validation result for a specific product.")[] | List of product validation results. | Big, 67.0 | 67.0 |
