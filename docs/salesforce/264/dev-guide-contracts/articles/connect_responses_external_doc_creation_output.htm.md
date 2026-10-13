---
page_id: connect_responses_external_doc_creation_output.htm
title: External Document Creation Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_external_doc_creation_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# External Document Creation Output

Output representation for the create external document
    request.

    

## Properties

      
      

          

          

          

          

          

        

          

          

          

          

          

        

          

          

          

          

          

        

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `externalDocumentDetails` | Object | Details of the external document record that is created. | Small, 58.0 | 58.0 |
| `isSuccess` | Boolean | Indicates whether the external document is created successful (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `message` | String | Provides a description of the error message in case of failure | Small, 58.0 | 58.0 |
| `ssoLinkUrl` | String | *<Need description>.* | Small, 58.0 | 58.0 |

    

    

## JSON Example

      
      

```
{
  "isSuccess": true,
  "message": "",
  "ssoLinkUrl": "",
  "ExternalDocumentDTO": {
    "contentVersionId": "",
    "ExternalDocumentId": "",
    "ExternalUserId": "",
    "referenceObjectId": "",
    "referenceObjectType": "",
    "url": "",
    "eTag": ""
  }
}
```
