---
page_id: connect_requests_context_definition_filter_list_input.htm
title: Context Definition Filter List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_list_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Definition Filter List Input

Input representation for a list of Context Definition Filters

JSON example
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
