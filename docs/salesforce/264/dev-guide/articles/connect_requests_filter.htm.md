---
page_id: connect_requests_filter.htm
title: Filter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Filter Input

Input representation of the filter request.

    
      
        
          

**JSON example**

          
: 
            

```

"filter": 
{
"criteria": [ {  
"property": "name",   
"operator": "eq",   
"value": "iPhone"
},
{
"criteriaType": "CustomWhereCondition",
"value": "(effectiveenddate = null OR effectiveenddate >= 2024-06-25)"
}
]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `criteria` | [Criteria](./connect_requests_criteria.htm.md)[] | Details of the filter criteria. | Required if the `filter` property is specified. | 60.0 |
