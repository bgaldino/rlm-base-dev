---
page_id: connect_responses_decision_table_data_output.htm
title: Decision Table Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_data_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Data

Output representation of the status of an action performed.

        
          

**Sample Output**

          
: 
            

```
{
  "errors": [],
  "errorFileId": "string_value"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​FileId` | String | Error code if transaction failed for any reason. | Small, 62.0 | 62.0 |
| `errors` | String[] | List of error messages if transaction failed for any reason. | Small, 62.0 | 62.0 |
