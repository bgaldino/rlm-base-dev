---
page_id: connect-responses-context-definition-info
title: Context Definition Information
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-info.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_definition_info.htm
fetched_at: 2026-11-25
---

# Context Definition Information

Output representation of context definition information.

**Sample Response**

: 

```
{
  "activeVersionId": "11pxx0000004cLEAAY",
  "contextDefinitionId": "11Oxx0000006XWfEAM",
  "contextTtl": 30,
  "createdBy": "Admin User",
  "createdDate": "2024-10-17T14:34:26.000Z",
  "definition": "ExampleDefinition",
  "description": "Example Description",
  "developerName": "ExampleDevelopername",
  "isActive": false,
  "isEditable": true,
  "isSuccess": true,
  "lastModifiedBy": "Admin User",
  "lastModifiedDate": "2024-10-17T14:34:26.000Z",
  "startDate": "2024-10-17T14:34:26.000Z"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `activeVersionId` | String | Active context definition version ID. | Small, 59.0 | 59.0 |
| `contextDefinitionId` | String | ID of the context definition. | Small, 59.0 | 59.0 |
| `contextTtl` | Integer | TTL of the context. | Small, 59.0 | 59.0 |
| `createdBy` | String | User who created the context definition. | Small, 59.0 | 59.0 |
| `createdDate` | String | Date on which the context definition was created. | Small, 59.0 | 59.0 |
| `definition` | String | Name of the context definition. | Small, 59.0 | 59.0 |
| `description` | String | Short description of context definition. | Small, 59.0 | 59.0 |
| `developerName` | String | Developer name associated with the definition. | Small, 59.0 | 59.0 |
| `isActive` | Boolean | Specifies if the context definition list is active (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isEditable` | Boolean | Specifies if the context definition list is editable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `lastModifiedBy` | String | User who last modified the definition. | Small, 59.0 | 59.0 |
| `lastModifiedDate` | String | Date on which the definition was modified last. | Small, 59.0 | 59.0 |
| `startDate` | String | Start date from when context definition is valid. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-info.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
