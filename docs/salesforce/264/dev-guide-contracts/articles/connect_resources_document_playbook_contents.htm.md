---
page_id: connect_resources_document_playbook_contents.htm
title: Document Playbook Contents (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_playbook_contents.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_document_playbook_resources.htm
fetched_at: 2026-10-13
---

# Document Playbook Contents (GET)

Get the playbook content chunks that match a user query by using
      vector similarity search.

    
      

This resource identifies the playbook mapping and the active playbook version for the
        specified record, runs a vector similarity search over the playbook content with the query
        text, and returns the matching content chunks with their metadata. To search against a
        specific playbook version and bypass the mapping and active-version lookup, pass
          `documentPlaybookVersionId`.

    

    

## Special Access Rules

      
      

Playbook must be enabled in your org, and you must have access to at least one
                    playbook.

    

    

## Resource

      
      

```
/connect/document-playbook/document-playbook-contents
```

    

    

## Resource Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/document-playbook/document-playbook-contents?recordId=800xx0000004C92GAE&userQueryString=termination+notice+period&chunkLimit=10
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

GET

    

    

## Request Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `recordId` | String | Entity ID of the object. | Required | 68.0 |
| `user​QueryString` | String | Text from the document to query against the playbook chunks. | Required | 68.0 |
| `chunkLimit` | Integer | Total number of matching chunks to fetch. The default value is 10. The maximum value is 100. | Optional | 68.0 |
| `documentPlaybook​VersionId` | String | ID of a specific `DocumentPlaybookVersion` to use for the search. When provided, the record-type, assignment, and active-version lookup chain is skipped and the search runs against this version directly. | Optional | 68.0 |

    

    

## Response Body for GET

      
      

[Playbook
              Contents](./connect_responses_playbook_contents_output.htm.md)
