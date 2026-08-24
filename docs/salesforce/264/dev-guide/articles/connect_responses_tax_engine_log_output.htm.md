---
page_id: connect_responses_tax_engine_log_output.htm
title: Tax Engine Log
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_engine_log_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Tax Engine Log

Output representation of the logs that the tax engine generates.

    

        
          

**JSON example**

          
: 
            

```
{
  "taxEngineLogs": [
    {
      "createdDate": "2022-03-09T10:55:38.000Z",
      "id": "3l1xx00000000PpAAI",
      "resultCode": "Success"
    }
  ]
}

```

          

        
      

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `createdDate` | String | Date when the tax engine creates the log. | Big, 62.0 | 62.0 |
| `id` | String | ID of the tax engine log record. | Big, 62.0 | 62.0 |
| `resultCode` | String | Result code associated with the created log. | Big, 62.0 | 62.0 |
