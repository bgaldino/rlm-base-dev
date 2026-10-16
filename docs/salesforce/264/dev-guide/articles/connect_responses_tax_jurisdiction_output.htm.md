---
page_id: connect_responses_tax_jurisdiction_output.htm
title: Tax Jurisdiction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_jurisdiction_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Tax Jurisdiction 

Output representation of the details of the tax jurisdiction for the tax
    line.

        
          

**JSON example**

          
: 
            

```
{
    "country": "US",
    "id": "63000",
    "level": "CIT",
    "name": "SEATTLE",
    "region": "WA",
    "stateAssignedNo": "1726"
}

```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `country` | String | Country of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `id` | String | ID of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `level` | String | Level of the tax jurisdiction, for example, `State` and `Federal`. | Big, 62.0 | 62.0 |
| `name` | String | Name of the tax jurisdiction authority. | Big, 62.0 | 62.0 |
| `region` | String | Parent region of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `stateAssigned​No` | String | Number of the assigned state. | Big, 62.0 | 62.0 |
