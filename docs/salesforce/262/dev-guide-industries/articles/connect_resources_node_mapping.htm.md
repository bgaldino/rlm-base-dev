---
page_id: connect_resources_node_mapping.htm
title: Context Node Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_node_mapping.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Node Mapping (POST, PATCH)

Create and update context node mappings.

Resource
:   ```
    /connect/context-mappings/${contextMappingId}/context-node-mappings
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings
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
            "contextNodeMappings": [
                {
                    "contextNodeId": "11oxx000001G31BAAS",
                    "sObjectName": "Order"
                },
                {
                    "contextNodeId": "11oxx000001G31CAAS",
                    "sObjectName": "OrderItem"
                }
            ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `attributeMappings` | [Context Attribute Mappings Input](./connect_requests_context_attribute_mappings_input.htm.md "Input representation of context attribute mapping.")[] | List of context attribute mappings. | Required | 59.0 |
        | `contextNodeId` | String | Reference to context node. | Optional | 59.0 |
        | `contextNodeMappingId` | String | ID of this context node mapping. Required for update. | Required | 59.0 |
        | `sObjectName` | String | SObject name. | Optional | 59.0 |

Response body for POST
:   [Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md "Output representation of list of context node mappings.")

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextNodeMappings": [
                {
                    "contextNodeMappingId": "11bxx000000YZipAAG",
                    "sObjectName": "Quote"
                },
                {
                    "contextNodeMappingId": "11bxx000000YZiqAAG",
                    "sObjectName": "QuoteItem"
                }
            ]
        }
        ```

Response body for PATCH
:   [Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md "Output representation of list of context node mappings.")
