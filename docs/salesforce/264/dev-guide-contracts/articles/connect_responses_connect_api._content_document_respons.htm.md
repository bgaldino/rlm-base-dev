---
page_id: connect_responses_connect_api._content_document_respons.htm
title: Content Document Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_connect_api._content_document_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Content Document Response

Output representation of the individual content documents.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `content​DocumentId` | String | Record ID of the content document. | Small, 60.0 | 60.0 |
| `contentDocument​LinkId` | String | Record ID of the content document link. | Small, 60.0 | 60.0 |
| `contractDocument​VersionId` | String | Record ID of the linked ContractDocumentVersion object. | Small, 60.0 | 60.0 |
| `created​Date` | String | Creation date of the content document. | Small, 60.0 | 60.0 |
| `file​Extension` | String | File extension of the content document. | Small, 60.0 | 60.0 |
| `isShared​Externally` | Boolean | Indicates if the file can be viewed by all users (`true`) or not (`false`). The default value is true. | Small, 60.0 | 60.0 |
| `lastModified​Date` | String | Last modification date of the content document. | Small, 60.0 | 60.0 |
| `title` | String | Title of the content document. | Small, 60.0 | 60.0 |

    

    

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
