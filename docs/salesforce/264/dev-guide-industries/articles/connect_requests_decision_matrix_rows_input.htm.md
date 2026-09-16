---
page_id: connect_requests_decision_matrix_rows_input.htm
title: Decision Matrix Rows Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_rows_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Rows Input

Input representation of the information to manage rows in relation to
      the decision matrix version.

      
        
          

**JSON Example**

          
: 
            

Add a row:

            

```
{
  "rows": [
    {
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "2000"
      }
    }
  ]
}

```

          

          
: 
            

Delete a row:

            

```
{
  "rows": [
    {
      "id": "a1j5w000006D04uAAC",
      "action": "delete",
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "2000"
      }
    }
  ]
}

```

          

          
: 
            

Update a row:

            

```
{
  "rows": [
    {
      "id": "a1j5w000006D04uAAC",
      "action": "update",
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "1500"
      }
    }
  ]
}

```

          

          
: 
            

Add row using a CSV file:

          

          
: 
            

```
{
   "fileId" : "f1j5w000005D04uFGC"
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

#### 

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fileId` | String | The ID of the [Content Document Version](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_contentversion.htm) that contains the rows details to be added or updated in a decision matrix version. | Optional Note This field is required if you’re using a CVS file to add or update rows. | 53.0 |
| `rows` | [Decision Matrix Row Input](./connect_requests_decision_matrix_row_input.htm.md)[] | List of rows to be added, updated, or deleted in a decision matrix version. | Required | 53.0 |
