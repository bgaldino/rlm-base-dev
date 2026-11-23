---
page_id: connect_responses_context_node.htm
title: Context Node
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_node.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Node

Output representation of the details of context nodes.

## JSON Example

```
{
  "contextNodes": [
    {
      "attributes": [],
      "baseReference": "11oxx000001G1DTPP88",
      "canonicalNodeId": "11oxx000001G1CGAA0",
      "childNodes": [],
      "contextDefinitionVersionId": "11pxx0000004UvYAAU",
      "contextNodeId": "11oxx000001G3xEAAS",
      "displayName": "Mobile_Contact_AccountSibRef",
      "isSuccess": true,
      "isTransposable": false,
      "name": "Mobile_Contact_AccountSibRef",
      "parentNodeId": "11oxx000001G1AeAAK",
      "tags": []
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | [Context Attribute List](./connect_responses_context_attribute_list.htm.md "Output representation of list of context attributes.")[] | List of attributes. | Small, 59.0 | 59.0 |
| `baseReference` | String | Identifies the context node ID of the parent context definition that this context node is inherited from. | Small, 60.0 | 60.0 |
| `canonicalNodeId` | String | ID of the canonical node that’s used as a reference to create this context node. | Small, 61.0 | 61.0 |
| `childNodes` | [Context Node Output](# "Output representation of the details of context nodes.")[] | List of child context nodes. | Small, 59.0 | 59.0 |
| `contextDefinition​VersionID` | String | ID of context definition version. | Small, 59.0 | 59.0 |
| `contextNodeID` | String | ID of this context node. | Small, 59.0 | 59.0 |
| `displayName` | String | Name of the context node that appears on the UI. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Specifies if the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isTransposable` | Boolean | Specifies if the context node is used for the transposable feature (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `name` | String | Name of the context node. | Small, 59.0 | 59.0 |
| `parentNodeId` | String | ID of (parent) context node. | Small, 59.0 | 59.0 |
| `tags` | [Context Attribute Tag Output](./connect_responses_context_attribute_tag.htm.md "Output representation of context attribute tag.")[] | List of tags. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_node.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
