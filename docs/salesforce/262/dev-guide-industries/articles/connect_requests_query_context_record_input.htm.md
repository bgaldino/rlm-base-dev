---
page_id: connect_requests_query_context_record_input.htm
title: Query Context Record Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_query_context_record_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Query Context Record Input

Input representation of query context record.

JSON example
:   ```
    {
      "contextId": "7bc695bc-f38b-4a94-8a95-0caa50f3da53"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `attributes` | String[] | List of attributes to be retrieved. | Optional | 58.0 |
    | `businessObjectTypeFilter` | String | Filter based on a business object type. | Optional | 58.0 |
    | `contextId` | String | The ID of the context to be queried. | Required | 58.0 |
    | `queryPath` | String[] | Path to the parent node. | Optional | 58.0 |
