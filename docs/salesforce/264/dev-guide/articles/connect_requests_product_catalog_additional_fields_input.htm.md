---
page_id: connect_requests_product_catalog_additional_fields_input.htm
title: Additional Fields Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_catalog_additional_fields_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Additional Fields Input

Input representation of the additional standard or custom fields to be included in the
    response.

    
      
        
          

**JSON example**

          
: 

```
"additionalFields": {
    "Product2": {
      "fields": [
        "code__c"
      ]
    }
```

This example shows a sample request with attribute definition field
            details.

```
"additionalFields":{
  "OptOutAssetization":true
  "OptOutDecompositionAction":false
  "OptOutSupplementalAction":false
}
```

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | String[] | List of additional standard or custom fields to be included in the response. | Required | 61.0 |
