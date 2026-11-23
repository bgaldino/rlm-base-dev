---
page_id: connect_responses_context_definition_interface.htm
title: Context Definition Interface
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Definition Interface

Output representation of the details of the context definition interface.

## JSON Example

```
{
  "contextDefinitionInterfaceMetadata": {
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
  },
  "contextDefinitionInterfaceNodeTagList": [
    {
      "attributeTags": [
        {
          "dataType": "STRING",
          "isMappingRequired": true,
          "isNodeTag": false,
          "tagName": "id_attr_tag"
        }
      ],
      "childNodeTags": [
        {
          "attributeTags": [
            {
              "dataType": "STRING",
              "isMappingRequired": false,
              "isNodeTag": false,
              "tagName": "contactId_attr_tag"
            },
            {
              "dataType": "STRING",
              "isMappingRequired": true,
              "isNodeTag": false,
              "tagName": "contactName_attr_tag"
            }
          ],
          "childNodeTags": [],
          "isMappingRequired": false,
          "isNodeTag": true,
          "tagName": "Contact_node_tag"
        }
      ],
      "isMappingRequired": true,
      "isNodeTag": true,
      "tagName": "Account_node_tag"
    }
  ],
  "isSuccess": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinition​InterfaceMetadata` | [Context Definition Interface Metadata](./connect_responses_context_definition_interface_metadata.htm.md "Output representation of the metadata associated with the context definition interface.") | Metadata details associated with the context definition interface. | Small, 62.0 | 62.0 |
| `contextDefinition​Interface​NodeTagList` | [Context Definition Interface Node Tag](./connect_responses_context_definition_interface_node_tag.htm.md "Output representation of the tags associated with the context definition interface.")[] | List of tags associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
