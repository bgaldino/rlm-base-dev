---
page_id: connect-responses-context-mapping-list
title: Context Mapping List Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-mapping-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_mapping_list.htm
fetched_at: 2026-11-25
---

# Context Mapping List Output

Output representation of a list of context mappings.

**Sample Response**

: 

```
{
  "contextMappingListId": "915c3ffc-65e6-47fd-b9c1-3fdfa92421c1",
  "contextMappings": [
    {
      "contextDefinitionVersionId": "11pxx0000004UcCAAU",
      "contextMappingId": "11jxx0000004LYBAA2",
      "contextNodeMappings": [],
      "description": "mappingDescription",
      "intents": [
        "ASSOCIATION",
        "HYDRATION",
        "PERSISTENCE",
        "TRANSLATION"
      ],
      "isDefault": false,
      "isInputMapped": false,
      "name": "mappingName"
    }
  ],
  "isSuccess": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextMappingListId` | String | Unique ID of the context mapping list. | Small, 59.0 | 59.0 |
| `contextMappings` | [Context Mapping Output[]](./connect-responses-context-mapping.md) | List of context mappings. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-mapping-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
