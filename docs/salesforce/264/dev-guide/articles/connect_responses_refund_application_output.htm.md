---
page_id: connect_responses_refund_application_output.htm
title: Refund Application
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_refund_application_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_responses_refund_credit_memo_output.htm
fetched_at: 2026-09-29
---

# Refund Application

Output representation of a single refund application record created by the refund against a credit memo API.

    

## JSON Example

      
      

```
{
  "applicationId": "4sFxx00000002ppEAA",
  "appliedToId": "a1Yxx0000004C95"
}
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `application​Id` | String | ID of the created application junction entity (`CreditMemoRefund` or `CreditMemoLineRefund`). | Big, 68.0 | 68.0 |
| `applied​To​Id` | String | ID of the record that the refund was applied to (the credit memo or a credit memo line). | Big, 68.0 | 68.0 |
