---
page_id: connect_responses_billing_batch_scheduler.htm
title: Billing Batch Scheduler
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_batch_scheduler.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Batch Scheduler

Output representation of the details of a created invoice or payment
    scheduler.

        
          

**JSON example**

          
: 
            

```
    "billingBatchScheduler": {
        "id": "5BSxx0000004TwGGAU"
    }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the invoice or payment scheduler. | Big, 62.0 | 62.0 |
