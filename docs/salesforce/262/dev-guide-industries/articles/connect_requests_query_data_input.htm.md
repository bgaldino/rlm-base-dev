---
page_id: connect_requests_query_data_input.htm
title: Query Record Status Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_query_data_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Query Record Status Input

Input representation of status and related error messages of query data
records.

JSON example
:   ```
    {
        "queryRecordStatusInput": {
            "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
            "queryPaths": [
                {
                    "dataPath": [
                        "TestOrder123"
                    ]
                }
            ]
        }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `queryRecordStatusInput` | Object | Input representation for context ID and the list of paths for querying the status. | Required | 59.0 |
