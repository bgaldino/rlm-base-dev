---
page_id: connect_responses_configurator_product_recommendation_output.htm
title: Configurator Product Recommendations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_recommendation_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configurator Product Recommendations

Output representation of the details of the product recommendations.

      
        
          

**JSON Example**

          
: 
            

```
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
