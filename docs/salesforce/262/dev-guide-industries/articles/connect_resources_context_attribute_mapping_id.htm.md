---
page_id: connect_resources_context_attribute_mapping_id.htm
title: Context Attribute Mapping ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_attribute_mapping_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Attribute Mapping ID (GET, DELETE)

Query and delete a context attribute mapping using an ID.

Resource
:   ```
    /connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${{contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, DELETE

Response body for GET
:   [Context Attribute Mapping Output](./connect_responses_context_attribute_mapping.htm.md "Output representation of the context attribute mapping.")
