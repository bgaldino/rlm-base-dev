---
page_id: connect-responses-context-node-list
title: Context Node List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-node-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_node_list.htm
fetched_at: 2026-11-25
---

# Context Node List

Output representation of the list of context nodes.

## JSON Example

```
{
  "contextNodeListId": "ebaf2554-88f2-4cb2-8418-cd3c250a9535",
  "contextNodes": [
    {
      "attributes": [
        {
          "attributeTags": [],
          "contextAttributeId": "11nxx000001hJm5AAE",
          "dataType": "REFERENCE",
          "domainSet": "Contact_AccountSibRef",
          "fieldType": "INPUT",
          "isKey": false,
          "isValue": false,
          "name": "ParentReference",
          "parentNodeId": "11oxx000001G3xEAAS"
        }
      ],
      "canonicalNodeId": "11oxx000001G1CGAA0",
      "childNodes": [],
      "contextDefinitionVersionId": "11pxx0000004UvYAAU",
      "contextNodeId": "11oxx000001G3xEAAS",
      "displayName": "Mobile_Contact_AccountSibRef",
      "isTransposable": false,
      "name": "Mobile_Contact_AccountSibRef",
      "parentNodeId": "11oxx000001G1AeAAK",
      "tags": []
    }
  ],
  "isSuccess": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextNode​ListId` | String | Unique ID of the context node list, which is required for Salesforce Lightning Design System (LDS). | Small, 59.0 | 59.0 |
| `contextNodes` | [Context Node []](./connect-responses-context-node.md) | List of context nodes. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-node-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
