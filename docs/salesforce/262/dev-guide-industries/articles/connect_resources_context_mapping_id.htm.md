---
page_id: connect_resources_context_mapping_id.htm
title: Context Mapping Id (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_mapping_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Mapping Id (GET, DELETE)

Query and delete a context mapping using an Id.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-mappings/${contextMappingId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-mappings/${contextMappingId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-mappings/${contextMappingId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, DELETE

Response body for GET
:   [Context Mapping Output](./connect_responses_context_mapping.htm.md "Output representation of context mapping.")
