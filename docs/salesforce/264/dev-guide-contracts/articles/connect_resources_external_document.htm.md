---
page_id: connect_resources_external_document.htm
title: External Documents (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_external_document.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_external_document_resources.htm
fetched_at: 2026-11-23
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

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=clm_developer_guide)

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

[External Document Output](./connect_responses_external_document_output.htm.md "Output representation of the details of an external document.")

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

[External Document Creation Output](./connect_responses_external_doc_creation_output.htm.md "Output representation for the create external document request.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_external_document.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
