---
page_id: connect_resources_create_query_tag.htm
title: Query Tags (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_query_tag.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Query Tags (POST)

Create query tags within a defined context

Resource
:   ```
    /connect/contexts/query-tags
    ```

Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts/query-tags
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
          "tags": [
            "Order"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextId` | String | ID of the context record. | Required | 59.0 |
        | `tags` | String[] | List of query tags to be queried within this context. | Required | 59.0 |

Response body for POST
:   [Query Tags
    Result](./connect_responses_query_tags_result.htm.md "Output representation of the results when querying context tags.")
