---
page_id: connect_resources_context_runtime_schema.htm
title: Context Runtime Schema (DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_runtime_schema.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Context Runtime Schema (DELETE)

Clear runtime schema cache for context definitions and their associated mappings.

Resource
:   ```
    /connect/context-runtime-schema/clear
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/context-runtime-schema/clear?contextDefinitionDevlName=CustomerProfile&contextMappingNames=StandardMapping,CustomMapping
    ```

Available version
:   65.0

HTTP methods
:   DELETE

Request parameters for DELETE
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextDefinitionDevlName` | String | Developer name of the context definition whose runtime schema is to be cleared. | Required | 65.0 |
    | `contextMappingNames` | String[] | Comma-separated list of mapping names to clear. If not provided, the default mapping for the definition is cleared. | Optional | 65.0 |

Response body for DELETE
:   This resource uses query parameters only and returns HTTP 204 No Content on
    success.
