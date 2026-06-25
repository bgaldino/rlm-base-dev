---
page_id: connect_resources_context_definition_id.htm
title: Context Definition Id (GET, PATCH, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-06-25
---

# Context Definition Id (GET, PATCH, DELETE)

Query, update, and delete a context definition using an ID.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
    ```

Example for DELETE
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, PATCH, DELETE

Response body for GET
:   [Context Definition Output](./connect_responses_context_definition.htm.md "Output representation of context definition.")

Request body for PATCH
:   JSON example
    :   ```
        {
        "definition": "Example Defintion patch",
        "description": "Example Description patch"
        }
        ```

Response body for PATCH
:   [Context Definition Information](./connect_responses_context_definition_info.htm.md "Output representation of context definition information.")
