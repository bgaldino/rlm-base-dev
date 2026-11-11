---
page_id: connect_responses_document_clause_set_list_respons.htm
title: Document Clause Set List Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_clause_set_list_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Document Clause Set List Response

Output representation for the list of document clause
    set.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `documentClauseSets` | [Document Clause Set Response[]](./connect_responses_document_clause_set_respons.htm.md) | The list of document clause set. | Small, 57.0 | 57.0 |

    

    

## JSON Example

      
      

```

{
  "documentClauseSets": [
    {
      "id": "123",
      "name": "Governing Law",
      "category": "00x40Axgdg0538F",
      "categoryName": "Confidential",
      "defaultLanguage": "English",
      "status": "Active"
    },
    {
      "id": "124",
      "name": "Governing Market Place",
      "category": "00x40Axgdg0538F",
      "categoryName": "Confidential",
      "defaultLanguage": "English",
      "status": "Active"
    }
  ]
}
```
