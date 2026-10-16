---
page_id: connect_resources_document_clause_sets.htm
title: Document Clause Sets
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_clause_sets.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clause_library_resources.htm
fetched_at: 2026-10-13
---

# Document Clause Sets

Get document clause sets as per specified filters.

    

## Resource

      
      

```
/connect/clause-library/document-clause-sets
```

    

    

## Example URI

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/68.0/connect/clause-library/document-clause-sets
```

    

    

## Available Version

      
      

57.0

    

    

## HTTP Methods

      
      

GET

    

    

## Query Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `category` | String | The comma-separated category values used for filtering. | Required | 57.0 |
| `defaultLanguage` | String | The comma-separated language values used for filtering. | Required | 57.0 |
| `name` | String | The name of the clause set used for filtering. | Required | 57.0 |
| `status` | String | The comma-separated status values used for filtering. | Required | 57.0 |

    

    

## Response Body for GET

      
      

[Document Clause Set List Response](./connect_responses_document_clause_set_list_respons.htm.md)
