---
page_id: connect_resources_query_context_interface_by_name.htm
title: Query Context Definition Interface By Name (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_interface_by_name.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Query Context Definition Interface By Name (GET)

Get the details of a context definition interface by using the context definition
interface name.

Resource
:   ```
    /connect/context-definition-interfaces/contextDefinitionInterfaceName
    ```
:   The contextDefinitionInterfaceName path parameter is the API name
    of the context definition interface.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definition-interfaces/exampleDefinitionInterface
    ```

Available version
:   62.0

HTTP methods
:   GET

Response body for GET
:   [Context Definition
    Interface](./connect_responses_context_definition_interface.htm.md "Output representation of the details of the context definition interface.")
