---
page_id: connect_responses_context_definition_interface_attribute_tag.htm
title: Context Definition Interface Attribute Tag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_attribute_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Definition Interface Attribute Tag

Output representation of the attribute tags associated with the context definition
interface.

## JSON Example

```
{
  "attributeTags": [
    {
      "dataType": "REFERENCE",
      "isMappingRequired": false,
      "isNodeTag": false,
      "domainName": "Account",
      "tagName": "AccountRef_attr_tag"
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataType` | String | Data type of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `domainName` | String | Domain name of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isMappingRequired` | Boolean | Indicates whether the attribute tag must be mapped in the context definition (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isNodeTag` | Boolean | Indicates whether the attribute tag is a node tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isOptional` | Boolean | Indicates whether validation must be done for the attribute tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `tagName` | String | Name of the attribute tag. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_attribute_tag.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
