---
page_id: connect_requests_clone_options_input.htm
title: Clone Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_clone_options_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Clone Options Input

Input representation of the options to clone a sales transaction.

    
      
        
          

**JSON example**

          
: This is a sample request to clone all line items in a ramped group within a sales
            transaction.

```
{
  "recordIds": ["0QLxx0000004CBYGA2"],
  "salesTransactionId": "0Q0xx0000004CE0CAM",
  "options": {
    "lineScope": "AllLines"
  }
}
```

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `recordTypeId` | String | ID of the record type related to the record to clone. | Optional | 65.0 |
| `lineScope` | String | Specifies the scope for cloning a ramp segment. You can clone only the last ramp segment. This property determines which line items must be cloned and added to the cloned segment. Valid values are: `AllLines`—Specifies whether all line items in a ramped group must be cloned. `RampedLinesOnly`—Specifies whether only the ramped line items must be cloned. A segment identifier is created for the newly cloned line items, ensuring date continuity between the existing and cloned segment. | Optional | 65.0 |
