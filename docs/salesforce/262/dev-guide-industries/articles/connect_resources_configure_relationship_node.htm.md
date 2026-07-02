---
page_id: connect_resources_configure_relationship_node.htm
title: Context Node Relationship (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_configure_relationship_node.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Node Relationship (POST)

Configure a relationship node by adding child context nodes to a specific context
node.

Resource
:   ```
    /connect/context-nodes/contextNodeId/configurerelationship
    ```
:   The contextNodeId specifies the ID of the context node to which you
    want to add the context nodes from the request body as child nodes.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/context-nodes/11oxx000001G3dtAAC/configurerelationship
    ```

Available version
:   61.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "contextNodeIds": [
            "11oxx000001G3dtAAC",
            "11oxx000001G3duAAC"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextNodeIds` | String | List of context node IDs to create the relationship nodes by adding them as child nodes to the context node that’s specified in the endpoint. | Required | 61.0 |

Response body for POST
:   [Context Node List](./connect_responses_context_node_list.htm.md "Output representation of the list of context nodes.")
