---
page_id: connect-requests-context-nodes-input
title: Context Nodes Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-nodes-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_nodes_input.htm
fetched_at: 2026-11-25
---

# Context Nodes Input

Input representation of context node.

## JSON Example

```
{
    "contextNodes": [
        {
            "name": "Node_0",
            "attributes": {
                "contextAttributes": [
                    {
                        "dataType": "STRING",
                        "fieldType": "INPUT",
                        "name": "Attribute_1"
                    }
                ]
            },
            "childNodes": {
                "contextNodes": [
                    {
                        "name": "Node_1",
                        "attributes": {
                            "contextAttributes": [
                                {
                                    "dataType": "NUMBER",
                                    "fieldType": "INPUT",
                                    "name": "Attribute_2"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | [Context Attributes Input](./connect-requests-context-attributes-input.md)[] | List of context attributes. | Optional | 59.0 |
| `childNodes` | [Context Nodes Input](./connect-requests-context-nodes-input.md)[] | List of child context nodes. | Optional | 59.0 |
| `contextNodeId` | String | ID of the context node. | Required | 59.0 |
| `isTransposable` | Boolean | Specifies if the context node is used for the transposable feature (`true`) or not (`false`). | Optional | 59.0 |
| `name` | String | Name of the context node. | Required | 59.0 |
| `parentNodeId` | String | ID of (parent) context node. | Optional | 59.0 |
| `tags` | [Context Tag Input](./connect-requests-context-tag-input.md)[] | List of context tags. | Optional | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-nodes-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
