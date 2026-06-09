---
page_id: connect_responses_product_discovery_product_selling_model_output.htm
title: Product Selling Model
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_product_selling_model_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Product Selling Model

Product Selling Model Component output representation

JSON example
:   ```
    {
      "productSellingModel": {
        "doesAutoRenewByDefault": false,
        "id": "0jPSG000000Avcv2AC",
        "name": "One Time",
        "sellingModelType": "OneTime",
        "status": "Active"
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `doesAutoRenewByDefault` | Boolean | Indicates whether the product is automatically renewed by default (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `id` | String | ID of the product selling model. | Small, 67.0 | 67.0 |
| `name` | String | Name of the product selling model. | Small, 67.0 | 67.0 |
| `pricingTerm` | Integer | Pricing term of the product selling model. | Small, 67.0 | 67.0 |
| `pricingTermUnit` | String | Pricing term unit of the product selling model. | Small, 67.0 | 67.0 |
| `sellingModelType` | String | Selling model type associated with the product selling model. | Small, 67.0 | 67.0 |
| `status` | String | Status of the product selling model. | Small, 67.0 | 67.0 |
