---
page_id: connect_responses_contract_document_version_c_c.htm
title: Contract Document Version CC Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_document_version_c_c.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Contract Document Version CC Response

Output representation of the latest details of a contract document version, including its
    ID, status, and associated documents and attachments.

    

## Properties

      
      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attachments` | [Content Document Response](./connect_responses_connect_api._content_document_respons.htm.md)[] | Details of the list of attachments associated with the contract document version. | Big, 60.0 | 60.0 |
| `contract​Documents` | [Content Document Response](./connect_responses_connect_api._content_document_respons.htm.md)[] | Details of the list of documents associated with the contract. | Big, 60.0 | 60.0 |
| `contract​Document​VersionId` | String | Record ID of the associated contract document version. | Small, 60.0 | 60.0 |
| `contract​Documents` | [Content Document Response](./connect_responses_connect_api._content_document_respons.htm.md)[] | Details of the list of documents associated with the contract. | Big, 60.0 | 60.0 |
| `contract​Id` | String | Record ID of the parent contract. | Small, 60.0 | 60.0 |
| `name` | String | Version name of the contract document version. | Small, 60.0 | 60.0 |
| `status` | String | Status of the contract document version. | Small, 60.0 | 60.0 |

    

    

## JSON Sample

      
      

```
{
  "contractId": "contractId_value",
  "contractDocumentVersionId": "contractDocumentVersionId_value",
  "status": "",
  "contractDocuments": [
    {
      "contentDocumentId": "contentDocumentId_value1",
      "contractDocumentVersionId": "contractDocumentVersionId_value1",
      "createdDate": "createdDate_value1",
      "fileExtension": "fileExtension_value1",
      "lastModifiedDate": "lastModifiedDate_value1",
      "title": "title_value1",
      "isSharedExternally": true
    }
  ],
  "attachments": [
    {
      "contentDocumentId": "contentDocumentId_value2",
      "contractDocumentVersionId": "contractDocumentVersionId_value2",
      "createdDate": "createdDate_value2",
      "fileExtension": "fileExtension_value2",
      "lastModifiedDate": "lastModifiedDate_value2",
      "title": "title_value2",
      "isSharedExternally": true
    }
  ]
}
```
