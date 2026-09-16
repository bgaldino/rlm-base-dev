---
page_id: connect_requests_decision_table_row_list_input.htm
title: Decision Table Row List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_row_list_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Row List Input

Input representation of the data for a row in the CSV based decision
      table that has to be added or updated.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "id": "1FIxx0000004CSOGA2",
  "rowData": {
    "City": "City3",
    "AssetLevel": "300"
  },
  "action": "update"
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | Action to perform on this row.Valid values are: `Create` `Update` | Optional | 62.0 |
| `id` | String | ID of the decision table tow. | Optional | 62.0 |
| `rowdata` | Map<String, Object> | Key value pair of the decision table row. | Required | 62.0 |
