---
page_id: connect-requests-context-meta-data-input
title: Context Metadata Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-meta-data-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_meta_data_input.htm
fetched_at: 2026-11-25
---

# Context Metadata Input

Input representation of context metadata.

## JSON Example

```
{
  "metadata": {
    "contextDefinitionId": "11Oxx0000006VjNEAU",
    "mappingId": "11jxx0000004Q83AAE"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | The ID of the context definition to use for validating and creating the context record. | Required | 59.0 |
| `mappingId` | String | The ID of the context mapping to use for resolving the provided context data attributes. | Required | 59.0 |
| `taggedData` | Boolean | Parameter to return tagged attribute names instead of raw names in the created context record. | Optional | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-meta-data-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
