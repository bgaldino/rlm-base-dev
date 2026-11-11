---
page_id: connect_resources_external_document_save.htm
title: External Documents Save
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_external_document_save.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_external_document_resources.htm
fetched_at: 2026-10-13
---

# External Documents Save

Save external documents.

    

## Resource

      
      

```
/connect/external-document/save
```

    

    

## Available Version

      
      

58.0

    

    

## Example for PUT

      
      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document?externalDocumentId=${externalDocumentId}&isAsync=false
```

    

    

## HTTP Methods

      
      

PUT

    

    

## Request Body for PUT

      
      

**JSON Example**

      

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

      

**Properties**

      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `externalDocumentId` | String | ID of an external document. | Required | 58.0 |
| `isAsync` | Boolean | Is Async | Required | 58.0 |
| `metadata` | [External Document Metadata](./connect_requests_external_document_metadata.htm.md) | Metadata | Optional | 58.0 |

    

    

## Response Body for PUT

      
      

[Save External Document Representation](./connect_responses_save_external_document.htm.md)
