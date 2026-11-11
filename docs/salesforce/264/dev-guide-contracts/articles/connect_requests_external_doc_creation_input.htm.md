---
page_id: connect_requests_external_doc_creation_input.htm
title: External Document Creation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_external_doc_creation_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# External Document Creation Input

Input representation of the request to create an external
      document.

    

## Properties

      
      

          

          

          

          

          

        

          

          

          

          

          

        

          

          

          

          

          

        

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentVersionId` | String | Content version ID of the document using which new external document is created. | Required | 58.0 |
| `documentNamePrefix` | String | Document name prefix, which is required to name the newly created external document. | Optional | 58.0 |
| `isAsync` | String | Determines the way the external document gets created. | Optional | 58.0 |
| `refObjectId` | String | ID of the reference object. This can be either a document template or a contract ID. | Optional | 58.0 |

    

    

## JSON Example

      
      

```

{
  "refObjectId": "",
  "contentversionId": "",
  "documentNamePrefix": "namespaceprefix",
  "isAsync": true
}
```
