---
page_id: connect_resources_context_node.htm
title: Context Node (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_node.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_node_management.htm
fetched_at: 2026-06-25
---

# Context Node (POST, PATCH)

Create and update context node.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-nodes
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-nodes
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-nodes
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST, PATCH

Request body for POST
:   JSON example
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
        | `childNodes` | [Context Nodes Input](./connect_requests_context_nodes_input.htm.md "Input representation of context node.")[] | List of child context nodes. | Optional | 59.0 |
        | `contextNodeId` | String | ID of the context node. | Required | 59.0 |
        | `isTransposable` | Boolean | Specifies if the context node is used for the transposable feature (`true`) or not (`false`). | Optional | 59.0 |
        | `name` | String | Name of the context node. | Required | 59.0 |
        | `parentNodeId` | String | ID of (parent) context node. | Optional | 59.0 |
        | `tags` | [Context Tag Input](./connect_requests_context_tag_input.htm.md "Input representation of the context tag.")[] | List of context tags. | Optional | 59.0 |

Response body for POST
:   [Context Node List Output](./connect_responses_context_node_list.htm.md "Output representation of the list of context nodes.")

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextNodes": [
                {
                    "name": "Node_0_patch",
                    "contextNodeId": "11oxx000001G9D2AAK"
                }
            ]
        }
        ```

Response body for PATCH
:   [Context Node List Output](./connect_responses_context_node_list.htm.md "Output representation of the list of context nodes.")
