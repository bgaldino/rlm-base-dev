---
page_id: connect_resources_context_service_runtime.htm
title: Context Service (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_service_runtime.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Context Service (DELETE, GET)

Retrieve the context details using a context ID. Delete a context record using a
context ID.

Resource
:   ```
    /connect/contexts/${contextId}
    ```

Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts/c4c69a9a-3841-4fc3-a10d-a52779ade3d8
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   DELETE, GET

Response body for GET
:   [Context Info](./connect_responses_context_info.htm.md "Output representation containing detailed information about a context.")

Response body for DELETE
:   None.
