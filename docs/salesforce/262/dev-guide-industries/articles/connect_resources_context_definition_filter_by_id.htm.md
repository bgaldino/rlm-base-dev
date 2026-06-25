---
page_id: connect_resources_context_definition_filter_by_id.htm
title: Context Definition Filter By ID (DELETE, GET, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_filter_by_id.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-06-25
---

# Context Definition Filter By ID (DELETE, GET, PATCH)

Get, update, or delete a context definition filter for a specified context definition
filter ID.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-filters/${contextDefinitionFilterId}
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions/SimpleDef/context-filters/1Tlxx0000004DUuCAM
    ```

Available version
:   65.0

HTTP methods
:   DELETE, GET, PATCH

Response body for GET
:   [Context Definition Filter](./connect_responses_context_definition_filter.htm.md "Output representation details of a context definition filter.")

Request body for PATCH
:   :   This example shows a sample request to
        create, get, or update a context definition filter.

        ```
        {
              "description": "Updated",
              "filterApiName": "FilterAccount",
              "filterName":"FilterAccount",
              "filtersPerNode": "{\"Account\":{\"filterCondition\":{\"attribute\":\"City\",\"operator\":\"EQUALS\",\"operands\":[{\"value\":\"Bengaluru\",\"type\":\"STRING\"}],\"composite\":false},\"orderByConditions\":[{\"orderByAttribute\":\"Name\",\"ascending\":false,\"nullsFirst\":false}],\"limit\":5}}",
              "contextDefinitionVersionId": "11pxx0000004VmmAAE"
            }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextDefinitionVersionId` | String | Unique identifier of the specific context definition version to which this filter belongs. | Required | 65.0 |
        | `description` | String | Details of the context definition filter such as the purpose of the filter. Use this field to document the filter's business logic, intended use case, or any important implementation details for future reference. | Optional | 65.0 |
        | `filterApiName` | String | Unique API name identifier for the context definition filter. | Required | 65.0 |
        | `filterName` | String | Display name for the context definition filter. | Required | 65.0 |
        | `filtersPerNode` | String | A JSON string representation of the filter condition logic that defines the filter criteria. This field contains the structured query conditions that's evaluated to determine which records match the filter. The JSON structure typically includes field names, operators, and values that form the filter expression. | Required | 65.0 |
        | `inheritedFrom` | String | Source context definition if filter is inherited in the GET request. This field is not applicable for POST request. | Optional | 65.0 |

Response body for PATCH
:   [Context Definition Filter](./connect_responses_context_definition_filter.htm.md "Output representation details of a context definition filter.")
