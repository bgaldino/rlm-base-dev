---
page_id: connect_requests_context_nodes_input.htm
title: Context Nodes Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_nodes_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Nodes Input

Input representation of context node.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `attributes` | [Context Attributes Input](./connect_requests_context_attributes_input.htm.md "Input representation of context attribute.") [] | List of context attributes. | Optional | 59.0 |
    | `childNodes` | [Context Nodes Input](# "Input representation of context node.")[] | List of child context nodes. | Optional | 59.0 |
    | `contextNodeId` | String | ID of the context node. | Required | 59.0 |
    | `isTransposable` | Boolean | Specifies if the context node is used for the transposable feature (`true`) or not (`false`). | Optional | 59.0 |
    | `name` | String | Name of the context node. | Required | 59.0 |
    | `parentNodeId` | String | ID of (parent) context node. | Optional | 59.0 |
    | `tags` | [Context Tag Input](./connect_requests_context_tag_input.htm.md "Input representation of the context tag.")[] | List of context tags. | Optional | 59.0 |
