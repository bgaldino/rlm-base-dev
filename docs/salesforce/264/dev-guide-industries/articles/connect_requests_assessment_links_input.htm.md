---
page_id: connect_requests_assessment_links_input.htm
title: Assessment Links Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_links_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Assessment Links Input

Associated assessments including id, category, reason and
      sequence.

    
      
        
          

**Root XML tag**

          
: `<assessmentLinks>`

        
        
          

**JSON example**

          
: 
            

```

  {
    "id": "0U3SG00000068Cb0AI",
    "category": "0iPSG0000024n0z2AA",
    "reason": "0iPSG0000024n0z2AA",
    "sequence": 333
  }
]
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required | Available Version |
| --- | --- | --- | --- | --- |
| `category` | String | The category that the supporting content belongs to. | No | 63.0 |
| `id` | String | The assessment used as the supporting content. | Yes | 55.0 |
| `reason` | String | The reason why the supporting content is required. | No | 63.0 |
| `sequence` | String | The sequence number of the content when multiple contents are available. | No | 63.0 |
