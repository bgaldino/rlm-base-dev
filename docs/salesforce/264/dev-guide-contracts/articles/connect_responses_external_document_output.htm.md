---
page_id: connect_responses_external_document_output.htm
title: External Document Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_external_document_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# External Document Output

Output representation of the details of an external
    document.

    

## Properties

      
      

          

          

          

          

          

        

          

          

          

          

          

        

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contentVersionId` | String | ID of the salesforce content version. | Small, 58.0 | 58.0 |
| `externalDocumentId` | String | ID of the external document record. | Small, 58.0 | 58.0 |
| `externalUserId` | String | ID of an external user. | Small, 58.0 | 58.0 |
| `referenceObject` | String | API name for salesforce reference object. | Small, 58.0 | 58.0 |
| `referenceObjectId` | String | ID of the salesforce reference object. | Small, 58.0 | 58.0 |
| `url` | String | URL for the external document. | Small, 58.0 | 58.0 |

    

    

## JSON Example

      
      

```

{
    "contentVersionId":"",
    "externalDocumentId":""
    "externalUserId":""
    "referenceObjectId":""
    "referenceObject":""//ContractDocumentVersion”, “DocumentTemplate"
    "url":""
}

```
