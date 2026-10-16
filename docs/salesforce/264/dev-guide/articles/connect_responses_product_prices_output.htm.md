---
page_id: connect_responses_product_prices_output.htm
title: Product Prices
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_prices_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Prices

Output representation of the details of the product prices.

        
          

**JSON example**

          
: 
            

```
{
  "prices": [
    {
      "currencyIsoCode": "USD",
      "isDefault": true,
      "isDerived": false,
      "isSelected": false,
      "price": 7.99,
      "priceBookEntryId": "01uSG000004wTsEYAU",
      "priceBookId": "01sSG00000DQCjhYAH",
      "pricingModel": {
        "id": "0jPSG000000Avcv2AC",
        "name": "One Time",
        "pricingModelType": "OneTime"
      }
    }
  ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `currencyIsoCode` | String | Currency ISO code of the given price. | Small, 67.0 | 67.0 |
| `effectiveFrom` | String | Date from when the given price is effective. | Small, 67.0 | 67.0 |
| `effectiveTo` | String | Date until when the given price is effective. | Small, 67.0 | 67.0 |
| `isDefault` | Boolean | Indicates whether the given price is default (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isDerived` | Boolean | Indicates whether the given price is derived (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isSelected` | Boolean | Indicates whether the given price is selected (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `price` | Double | Price of the product. | Small, 67.0 | 67.0 |
| `priceBookEntryId` | String | Price book entry ID of the given price. | Small, 67.0 | 67.0 |
| `priceBookId` | String | Price book ID of the given price. | Small, 67.0 | 67.0 |
| `pricingModel` | [Pricing Model](./connect_responses_pricing_model_output.htm.md)[] | Pricing model of the given price. | Small, 67.0 | 67.0 |
