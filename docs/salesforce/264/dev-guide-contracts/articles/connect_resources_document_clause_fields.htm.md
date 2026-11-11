---
page_id: connect_resources_document_clause_fields.htm
title: Document Clause Fields
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_clause_fields.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clause_library_resources.htm
fetched_at: 2026-10-13
---

# Document Clause Fields

Get distinct document clause values for a given fieldName parameter.

    

## Resource

      
      

```
/connect/clause-library/document-clauses/fields
```

    

    

## Example URI

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/68.0/connect/clause-library/document-clauses/fields?clauseSetId={id}
```

    

    

## Available Version

      
      

57.0

    

    

## HTTP Methods

      
      

GET

    

    

## Query Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `clauseSetId` | String | The ID of the document clause set. | Required | 57.0 |
| `fieldName` | String | Specifies language and name. Value is case-sensitive. Possible values are `Language` or `Name`. | Required | 57.0 |
| `language` | String | The language for the clauseSetId parameter. | Required | 57.0 |
| `name` | String | The name for the clauseSetId parameter. | Required | 57.0 |
| `status` | String | Displays records based on the status. | Required | 57.0 |

    

    

## Response Body for GET

      
      

[Document Clause Fields Response](./connect_responses_document_clause_fields_respons.htm.md)
