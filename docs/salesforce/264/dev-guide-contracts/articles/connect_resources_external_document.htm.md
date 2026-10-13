---
page_id: connect_resources_external_document.htm
title: External Documents (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_external_document.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_external_document_resources.htm
fetched_at: 2026-10-13
---

# External Documents (GET, POST)

Get information about external document details and
    update.

    

## Resource

      
      

```
/connect/external-document
```

    

    

## Example URI

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document
```

    

    

## Available Version

      
      

58.0

    

    

## Example for GET

      
      

#### Note

You can access the external document details using the reference object such as
                    document template, contract document version or using the external document ID.

      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document?externalDocumentId=${externalDocumentId}
```

      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document?refObjectId=${refObjectId}
```

      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document?externalDocumentId=${externalDocumentId}&refObjectId=${refObjectId}
```

    

    

## Example for POST

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v58.0/connect/external-document
```

    

    

## HTTP Methods

      
      

GET, POST

    

    

## Query Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `externalDocumentId` | String | ID of an external document record. | Required | 58.0 |
| `refObjectId` | String | ID for the salesforce reference object. | Required | 58.0 |

    

    

## Response Body for GET

      
      

[External Document Output](./connect_responses_external_document_output.htm.md)

    

    

## Request Body for POST

      
      

**JSON Example**

      

```

{
  "refObjectId": "",
  "contentversionId": "",
  "documentNamePrefix": "namespaceprefix",
  "isAsync": true
}
```

      

**Properties**

      

                          

                          

                          

                          

                          

                        

                          

                          

                          

                          

                          

                        

                          

                          

                          

                          

                          

                        

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentVersionId` | String | Content version ID of the document using which new external document is created. | Required | 58.0 |
| `documentNamePrefix` | String | Document name prefix, which is required to name the newly created external document. | Optional | 58.0 |
| `isAsync` | String | Determines the way the external document gets created. | Optional | 58.0 |
| `refObjectId` | String | ID of the reference object. This can be either a document template or a contract ID. | Optional | 58.0 |

    

    

## Response Body for POST

      
      

[External Document Creation Output](./connect_responses_external_doc_creation_output.htm.md)
