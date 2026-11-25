---
page_id: connect-responses-context-definition-interface-metadata-list
title: Context Definition Interface Metadata List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-interface-metadata-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_definition_interface_metadata_list.htm
fetched_at: 2026-11-25
---

# Context Definition Interface Metadata List

Output representation of the metadata list associated with the context definition interfaces.

## JSON Example

```
{
  "contextDefinitionInterfaceMetadataList": [
    {
      "createdBy": "Automated Process",
      "createdDate": "2024-05-15T00:00:00.000Z",
      "description": "Test Interface",
      "developerName": "TestBaseInterface",
      "interfaceName": "TestBaseInterface",
      "lastModifiedBy": "Automated Process",
      "parentInterfaces": [
        "TestBaseInterface1"
      ],
      "version": "62.1"
    }
  ],
  "contextDefinitionInterfaceMetadataListId": "43db7f18-9dd7-40a2-9a34-a2b3a1cff9e5",
  "isSuccess": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinition​Interface​MetadataList` | [Context Definition Interface Metadata](./connect-responses-context-definition-interface-metadata.md)[] | List of metadata associated with the context definition interfaces. | Small, 62.0 | 62.0 |
| `contextDefinition​Interface​MetadataListId` | String | Unique ID of the metadata list associated with the context definition interfaces. Required for Lightning Data Service (LDS). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-interface-metadata-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
