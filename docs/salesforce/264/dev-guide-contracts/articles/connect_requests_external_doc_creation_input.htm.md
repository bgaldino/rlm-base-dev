---
page_id: connect_requests_external_doc_creation_input.htm
title: External Document Creation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_external_doc_creation_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_external_doc_creation_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
