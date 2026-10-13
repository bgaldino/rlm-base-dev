---
page_id: connect_responses_document_clause_fields_respons.htm
title: Document Clause Fields Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_clause_fields_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Document Clause Fields Response

Output representation for the list of document clause
    fields.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fieldValues` | String[] | The values returned for the document clause fields based on the query parameter specified in the request. | Small, 57.0 | 57.0 |

    

    

## JSON Example

      
      

```

{
  "fieldValues": [
    "english",
    "spanish",
    "german"
  ]
}
```
