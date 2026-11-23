---
page_id: connect_responses_context_definition_interface_node_tag.htm
title: Context Definition Interface Node Tag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_node_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Definition Interface Node Tag

Output representation of the tags associated with the context definition
interface.

## JSON Example

```
{
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
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeTags` | [Context Definition Interface Attribute Tag](./connect_responses_context_definition_interface_attribute_tag.htm.md "Output representation of the attribute tags associated with the context definition interface.")[] | List of attribute tags associated with the context definition interface. | Small, 62.0 | 62.0 |
| `childNodeTags` | [Context Definition Interface Node Tag](# "Output representation of the tags associated with the context definition interface.")[] | List of child node tags associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isMappingRequired` | Boolean | Indicates whether the context tags must be mapped in the context definition (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isNodeTag` | Boolean | Indicates whether the context tag is a node tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isOptional` | Boolean | Indicates whether validation must be done for the context tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `tagName` | String | Name of the context tag. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_node_tag.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
