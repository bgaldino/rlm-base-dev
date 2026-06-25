---
page_id: connect_resources_context_node_mapping_id.htm
title: Context Node Mapping Id (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_node_mapping_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Node Mapping Id (GET, DELETE)

Query and delete a context node mapping using an ID.

Resource
:   ```
    /connect/context-mappings/${contextMappingId}/context-node-mappings/${contextNodeMappingId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings/${contextNodeMappingId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings/${contextNodeMappingId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, DELETE

Response body for GET
:   [Context Node Mapping Output](./connect_responses_context_node_mapping.htm.md "Output representation of the context node mapping.")
