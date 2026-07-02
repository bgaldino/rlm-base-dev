---
page_id: connect_resources_write_through_tags.htm
title: Write Through Tags (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_write_through_tags.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Write Through Tags (PATCH)

Update Context Attributes through tags.

Resource
:   ```
    /connect/contexts/write-through-tags
    ```

Available version
:   63.0

HTTP methods
:   PATCH

Request body for PATCH
:   ```
    {
        "contextId": "3ec8da809ebd6cef79f685239fb005e8c7cffa075a0d3d7b1d8d17ec22bxxxxd",
        "nodePathAndTagValues": [
            {
                "nodePath": {
                    "dataPath": [
                        "001xx000003GbQSAA0"
                    ]
                },
                "tagValues": [
                    {
                        "tagName": "Name",
                        "tagValue": "updatedAccount"
                    },
                    {
                        "tagName": "City",
                        "tagValue": "Bangalore"
                    }
                ]
            }
        ]
    }
    ```

Request parameters for PATCH
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextId` | String | ID of context which will get updated. | Required | 63.0 |
    | `nodePath​And​TagValues` | [List<Node​PathAndTag​ValuesInput​Representation>](./connect_requests_node_path_and_tag_values.htm.md "Input representation of the node path which needs to update with tag details.") | Node path which needs to update with tag details. | Required | 63.0 |

Response body for PATCH
:   [ContextOutputRepresentation](./connect_responses_context_output.htm.md "Output Representation of attributes associated with defined context.")
