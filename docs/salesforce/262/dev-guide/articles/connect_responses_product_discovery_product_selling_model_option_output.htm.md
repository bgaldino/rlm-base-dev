---
page_id: connect_responses_product_discovery_product_selling_model_option_output.htm
title: Product Selling Model Option
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_product_selling_model_option_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Product Selling Model Option

Output representation of the product selling model option component.

JSON example
:   ```
    {
      "productSellingModelOptions": [
        {
          "id": "0iOSG000000J64x2AC",
          "isDefault": true,
          "productId": "01tSG00000BiywkYAB",
          "productSellingModel": {
            "doesAutoRenewByDefault": false,
            "id": "0jPSG000000Avcv2AC",
            "name": "One Time",
            "sellingModelType": "OneTime",
            "status": "Active"
          },
          "productSellingModelId": "0jPSG000000Avcv2AC"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the product selling model option. | Small, 67.0 | 67.0 |
| `isDefault` | Boolean | Indicates whether this product selling model option is default (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `productId` | String | ID of the product. | Small, 67.0 | 67.0 |
| `productSellingModel` | [Product Selling Model](./connect_responses_product_discovery_product_selling_model_output.htm.md "Product Selling Model Component output representation")[] | Details of the product selling model. | Small, 67.0 | 67.0 |
| `productSellingModelId` | String | ID of the product selling model. | Small, 67.0 | 67.0 |
| `prorationPolicy` | [Proration Policy](./connect_responses_proration_policy_output.htm.md "Output representation of the details of the proration policy component.")[] | Details of the proration policy. | Small, 67.0 | 67.0 |
