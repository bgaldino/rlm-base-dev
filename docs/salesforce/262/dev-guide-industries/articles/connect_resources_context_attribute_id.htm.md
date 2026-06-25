---
page_id: connect_resources_context_attribute_id.htm
title: Context Attribute ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_attribute_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_attribute_management.htm
fetched_at: 2026-06-25
---

# Context Attribute ID (GET, DELETE)

Query and delete a context attribute using an ID.

Resource
:   ```
    /connect/context-nodes/${contextNodeId}/context-attributes/${contextAttributeId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-nodes/${contextNodeId}/context-attributes/${contextAttributeId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-nodes/${contextNodeId}/context-attributes/${contextAttributeId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, DELETE

Response body for GET
:   [Context Attribute Output](./connect_responses_context_attribute.htm.md "Output representation of the context attribute.")
