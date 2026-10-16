---
page_id: connect_responses_bre_decision_matrix_lookup_result.htm
title: Decision Matrix Lookup Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_decision_matrix_lookup_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Lookup Result

Output representation of the individual output of a decision matrix
      version lookup.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "outputs": [
    {
      "results": [],
      "error": "Input Data is Missing"
    },
    {
      "results": [
        {
          "name": "premium",
          "value": "2400"
        },
        {
          "name": "tax",
          "value": "300"
        }
      ]
    },
    {
      "results": [],
      "error": "There is no output for the given input data"
    }
  ]
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `outputs` | [Decision Matrix Lookup Basic Result](./connect_responses_decision_matrix_lookup_basic_result.htm.md)[] | List of outputs returned by a decision matrix. An output may contain multiple variables. | Small, 55.0 | 55.0 |
