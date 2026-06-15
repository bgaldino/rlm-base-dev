---
page_id: connect_responses_configurator_product_recommendation_output.htm
title: Configurator Product Recommendations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_recommendation_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Product Recommendations

Output representation of the details of the product recommendations.

JSON Example
:   ```
    {
      "productRecommendations": [
        {
          "referenceId": "CORE_BUNDLE_001",
          "productIds": [
            "01t000000001234",
            "01t000000005678"
          ]
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `productIds` | String[] | List of recommended product IDs. | Small, 65.0 | 65.0 |
| `referenceId` | String | Reference ID for the recommendation. | Small, 65.0 | 65.0 |
