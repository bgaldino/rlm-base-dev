---
page_id: connect_resources_context_query_lean_tag.htm
title: Context Query Tags Leaner (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_query_lean_tag.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_resources.htm
fetched_at: 2026-06-25
---

# Context Query Tags Leaner (POST)

Query tags and return a memory-optimized (leaner) result suitable for Apex and low-heap
clients. Eliminate redundant metadata to reduce heap usage and payload size.

Resource
:   ```
    /connect/contexts/query-tags-leaner
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts/query-tags-leaner
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   Root XML tag
    :   `<LeanerQueryTagsInputRepresentation>`

    JSON example
    :   ```
        {
          "contextId": "0000000s07fm061002917633740427233ff03037a8fe48048696667781ec824c",
          "tags": [
            "Contact_FirstName",
            "Contact_Email"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextId` | String | ID of the context to query. | Required | 66.0 |
        | `tags` | String[] | List of tag names to query from the context. Tags can include both attribute-level and node-level. | Required | 66.0 |

Response body for POST
:   [Leaner Query Tags Result](./connect_responses_leaner_query_tags_result.htm.md "Output representation of the leaner query tags result. The result includes compact tag data mapped to tag names and a shared list of record IDs.")
