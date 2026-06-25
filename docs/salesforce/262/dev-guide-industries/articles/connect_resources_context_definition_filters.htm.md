---
page_id: connect_resources_context_definition_filters.htm
title: Context Definition Filters (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_filters.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-06-25
---

# Context Definition Filters (GET, POST)

Create or get context filters associated with a specific context definition. Context
filters are criteria or conditions that refine or limit data operations based on specific
parameters.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-filters
    ```

    The
    `contextDefinitionId` property value is the unique
    identifier for the context definition whose filters you want to retrieve.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions/SimpleDef/context-filters
    ```

Available version
:   65.0

HTTP methods
:   GET, POST

Response body for GET
:   [Context Definition Filter List](./connect_responses_context_definition_filter_list.htm.md "Output representation details of context definition filter list.")

Request body for POST
:   JSON example
    :   ```
        {
          "filters": [
            {
              "filterApiName": "FilterAccount",
              "filterName":"FilterAccount",
              "filtersPerNode": "{\"Account\":{\"filterCondition\":{\"attribute\":\"City\",\"operator\":\"EQUALS\",\"operands\":[{\"value\":\"Bengaluru\",\"type\":\"STRING\"}],\"composite\":false},\"orderByConditions\":[{\"orderByAttribute\":\"Name\",\"ascending\":false,\"nullsFirst\":false}],\"limit\":5}}",
              "contextDefinitionVersionId": "11pxx0000004VmmAAE"
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `filters` | [Context Definition Filter Input](./connect_requests_context_definition_filter_input.htm.md "Input representation details of context definition filter.")[] | List of context definition filter inputs. | Required | 65.0 |

Response body for POST
:   [Context Definition Filter List](./connect_responses_context_definition_filter_list.htm.md "Output representation details of context definition filter list.")
