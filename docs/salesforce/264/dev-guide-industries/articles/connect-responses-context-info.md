---
page_id: connect-responses-context-info
title: Context Information
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-info.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_info.htm
fetched_at: 2026-11-25
---

# Context Information

Output representation containing detailed information about a context.

**Sample Response**

: 

```
{
  "childBusinessObjectTypes": [
    "Order"
  ],
  "contextDefinitionId": "11Oxx0000006VjNEAU",
  "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
  "contextMappingId": "11jxx0000004Q83AAE",
  "isSuccess": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `childBusinessObjectTypes` | String[] | List of associated child business object types. | Small, 59.0 | 59.0 |
| `contextDefinitionId` | String | ID of the context definition record. | Small, 59.0 | 59.0 |
| `contextId` | String | Unique ID of the context. | Small, 59.0 | 59.0 |
| `contextMappingId` | String | Identifier for the context’s mapping structure. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-info.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
