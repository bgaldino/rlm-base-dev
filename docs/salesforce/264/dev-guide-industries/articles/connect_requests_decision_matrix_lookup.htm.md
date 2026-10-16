---
page_id: connect_requests_decision_matrix_lookup.htm
title: Decision Matrix Lookup Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_lookup.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Lookup Input

Input representation of the input for a decision matrix
    lookup.

      
        
          

**JSON example**

          
: 
            

```
{
  "inputs": [
    {
      "input": [
        {
          "name": "Premium",
          "value": "2400"
        }
      ]
    },
    {
      "input": [
        {
          "name": "Tenure",
          "value": "10"
        }
      ]
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z"
  }
}
```

          

        
        
          
: Here, `Premium` and `Tenure` are column
            headers in the matrix, and `2400` and `10` are
            values of a cell in the column.

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | [Decision Matrix Input](./connect_requests_decision_matrix_input.htm.md) | List of inputs passed to a decision matrix. An input may contain multiple variables. | Required | 55.0 |
| `options` | [Decision Matrix Options Input](./connect_requests_decision_matrix_options.htm.md) | The lookup options for a decision matrix. | Optional | 55.0 |
