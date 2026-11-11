---
page_id: connect_requests_save_external_document_input.htm
title: Save External Document Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_save_external_document_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Save External Document Input 

Input representation to save external document to
    salesforce.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `externalDocumentId` | String | ID of an external document. | Required | 58.0 |
| `isAsync` | Boolean | Is Async | Required | 58.0 |
| `metadata` | [External Document Metadata](./connect_requests_external_document_metadata.htm.md) | Metadata | Optional | 58.0 |

    

    

## JSON Example

      
      

```

{
    "externalDocumentId" : "id",
    "isAsync" : "false", 
    "metadata": {
        "sections" : [
            {
                "guid": "guid1",
                "name": "test1",
                "isReadonly": false
            },
            {
                "guid": "guid2",
                "name": "test2",
                "isReadonly": false
            }
        ],
        "objectReferences" :[
            {
                "objectType": "clause",
                "objectId": "clauseid1",
                "usages": {
                    "sectionIds": [
                        "guid1",
                        "guid2"
                    ],
                    "usedInDocument": true
                }
            },
            {
                "objectType": "clause",
                "objectId": "clauseid2",
                "usages": {
                    "sectionIds": [
                        "guid1",
                        "guid2"
                    ],
                    "usedInDocument": false // points to if this object is used in document as well without sections
                }
            }
        ]
    }
}
```
