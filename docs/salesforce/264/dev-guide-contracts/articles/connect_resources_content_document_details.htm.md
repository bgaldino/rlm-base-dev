---
page_id: connect_resources_content_document_details.htm
title: Content Document Details (GET, DELETE, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_content_document_details.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-11-23
---

# Content Document Details (GET, DELETE, PATCH)

Get content document details associated with a contract document
version.
Delete content document details associated with a contract document
version.
Update the content document details associated with a contract document
version.

## Resource

```
/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/content-documents
```

## Available Version

56.0

## HTTP Methods

GET, DELETE, PATCH

## Example for GET

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract-document-version/$0qtXXXXXXX/content-documents
```

## Example for DELETE

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract-document-version/$0qtXXXXXXX}/content-documents?contentDocumentId=$069XXXXXXX
```

## Example for PATCH

```
https://YOUR_INSTANCE.salesforce.com/services/data/v60.0/connect/clm/contract-document-version/$0qtXXXXXXX/content-document?contentDocumentId=
069XXXXXXX&share=true
```

## Request Parameters for DELETE

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentDocumentId` | String | ID of the content document object created for an attachment. | Required | 56.0 |

## JSON Example for DELETE

```
{
    "contractDocumentVersionId": "0qtXXXXXXX" // The contractDocumentVersionId for which the attachment is to be Deleted.
    "contentDocumentId" : "069XXXXXXX" // The ContentDocumentId is ID of ContentDocument created for attachment
}
```

## Response Body for GET

[Content Document List](./connect_responses_content_document_list_respons.htm.md "Output representation of the content document record list.")

## Request Parameters for PATCH

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentDocumentId` | String | ID of the content document whose sharing status is being updated. | Required | 60.0 |
| `share` | Boolean | Indicates whether sharing is enabled (`true`) or disabled (`false`) for the content document. | Required | 60.0 |

## Response Body for PATCH

[Generic
Output](./connect_responses_generic_output.htm.md "Generic output response.")[]

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_content_document_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
