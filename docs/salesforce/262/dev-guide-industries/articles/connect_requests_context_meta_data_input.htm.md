---
page_id: connect_requests_context_meta_data_input.htm
title: Context Metadata Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_meta_data_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Metadata Input

Input representation of context metadata.

JSON example
:   ```
    {
      "metadata": {
        "contextDefinitionId": "11Oxx0000006VjNEAU",
        "mappingId": "11jxx0000004Q83AAE"
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextDefinitionId` | String | The ID of the context definition to use for validating and creating the context record. | Required | 59.0 |
    | `mappingId` | String | The ID of the context mapping to use for resolving the provided context data attributes. | Required | 59.0 |
    | `taggedData` | Boolean | Parameter to return tagged attribute names instead of raw names in the created context record. | Optional | 59.0 |
