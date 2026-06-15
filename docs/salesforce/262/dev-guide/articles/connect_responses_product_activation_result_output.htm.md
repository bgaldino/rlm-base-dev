---
page_id: connect_responses_product_activation_result_output.htm
title: Product Activation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_activation_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Product Activation Result

Output representation of the activation outcome for a single product, including any
errors that occurred while activating the product or its associated usage records.

JSON example
:   ```
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
| `errors` | [Usage Activation Error](./connect_responses_usage_activation_error_output.htm.md "Output representation of a single error encountered while activating a usage product or one of its related records.")[] | List of errors that occurred while activating the product or its associated usage records. | Big, 67.0 | 67.0 |
| `productId` | String | ID of the Product2 record that this activation outcome describes. | Big, 67.0 | 67.0 |
