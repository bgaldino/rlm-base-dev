---
page_id: connect_resources_template_doc_version.htm
title: Contract Document Version Template
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_template_doc_version.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# Contract Document Version Template

Change the template in a contract document version.

    

## Resource

      
      

```
/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

PATCH

    

    

## Example for PATCH

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract-document-version/${contractDocumentVersionId}
```

    

    

## Request Body for PATCH

      
      

**JSON Example**

      

```

{
  "templateId": "2dtxx000000004rAAA",
  "isExternalReviewImport": false,
  "externalReviewType": "OnlineMicrosoft365"
}
```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `external​Review​Type` | String | Type of external review. Possible values are `OnlineMicrosoft365` or `OfflineMicrosoftWord`. | Optional | 60.0 |
| `isExternal​Review​Import` | Boolean | Indicates whether the checkout is for an external review import (`true`) or not (`false`). | Optional | 59.0 |
| `pdf​Document​Id` | String | ID for Contract PDF document. | Optional | 56.0 |
| `templateId` | String | Template ID with key prefix 2dt used to generate document. | Required | 56.0 |
| `word​Document​Id` | String | ID for Contract word document. | Optional | 56.0 |

    

    

## Response Body for PATCH

      
      

[Document Generate Representation](./connect_responses_document_generate.htm.md)
