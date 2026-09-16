---
page_id: connect_responses_coupon_details.htm
title: Promotion Coupon
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_coupon_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Promotion Coupon

Output representation of the details of a coupon that's eligible for the recommended
    promotion.

        
          

**JSON example**

          
: 
            

```
{
  "coupon": {
    "couponCode": "COUPON_002",
    "endDateTime": null,
    "startDateTime": "2025-10-08T19:00:00.000Z",
    "status": "Active"
  }
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `couponCode` | String | Unique code of the coupon. | Big, 66.0 | 66.0 |
| `endDateTime` | String | End date and time of the coupon. | Big, 66.0 | 66.0 |
| `startDateTime` | String | Start date and time of the coupon. | Big, 66.0 | 66.0 |
| `status` | String | Status of the coupon. | Big, 66.0 | 66.0 |
