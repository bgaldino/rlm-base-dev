---
page_id: connect_requests_usage_activation_input.htm
title: Usage Product Activation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_activation_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Usage Product Activation Input

Input representation of a usage product activation request.

JSON example
:   ```
    {
      "shouldValidateProductSetup": false,
      "activationRequests": [
        {
          "productId": "01txx0000006i2gAAA",
          "usageResourceIds": [
            "0hUxx000000001",
            "0hUxx000000002"
          ]
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `activation​Requests` | [Usage Activation Request Input](./connect_requests_usage_activation_request_input.htm.md "Input representation for a single product entry in a usage product activation request. Each entry identifies one product and the usage resources to activate for that product.")[] | List of activation requests. Each entry identifies a product and the usage resources to activate for that product. This list accepts only one entry. If you include more, the API returns the `MAX_LIMIT_EXCEEDED` error. | Required | 67.0 |
    | `shouldValidate​ProductSetup` | Boolean | Indicates whether to run product setup validation before activation (`true`) or not (`false`). The default value is `true`. | Optional | 67.0 |
