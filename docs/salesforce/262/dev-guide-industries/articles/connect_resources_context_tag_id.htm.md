---
page_id: connect_resources_context_tag_id.htm
title: Context Tag ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_tag_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_tag_managament.htm
fetched_at: 2026-06-25
---

# Context Tag ID (GET, DELETE)

Query and delete a context tag.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-tags/${contextTagId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags/${contextTagId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags/${contextTagId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, DELETE

Response body for GET
:   [Context Attribute Tag Output](./connect_responses_context_attribute_tag.htm.md "Output representation of context attribute tag.")
