---
page_id: connect_resources_doc_generation_process.htm
title: Document Generation Process
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_doc_generation_process.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# Document Generation Process

Get the status of document generation process for a given contract
      document version ID. 

    

## Resource

      
      

```
/connect/clm/document-generation-process/status
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

GET

    

    

## Example for GET

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/document-generation-process/status?contractDocumentVersionId=<contractDocumentVersionId>
```

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractDocument​VersionId` | String | ID of the contract document version. | Required | 56.0 |

    

    

## Response Body for GET

      
      

[Document Generation ​Process Status
            Representation](./connect_responses_document_generation_process_status.htm.md)
