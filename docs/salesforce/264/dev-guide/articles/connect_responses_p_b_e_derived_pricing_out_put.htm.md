---
page_id: connect_responses_p_b_e_derived_pricing_out_put.htm
title: PBE Derived Pricing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_p_b_e_derived_pricing_out_put.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PBE Derived Pricing

Output representation of the response that includes the source product for the Price Book
    Entry (PBE) derived pricing.

        
          

**JSON example**

          
: 
            

```
{
"productId":"01txx0000006i2SAAQ",
"pricebookEntryId":"01uxx0000008yYcAAI",
"effectiveFrom":"2020-01-01T22:53:20.000Z",
"effectiveTo":"2021-01-01T22:53:20.000Z"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md)[] | Displays the error while processing the request. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `source​ProceductId` | String | ID of the source product. | Small, 61.0 | 61.0 |
