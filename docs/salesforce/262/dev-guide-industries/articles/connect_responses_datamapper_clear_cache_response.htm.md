---
page_id: connect_responses_datamapper_clear_cache_response.htm
title: Data Mapper Cache Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_datamapper_clear_cache_response.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_responses.htm
fetched_at: 2026-06-25
---

# Data Mapper Cache Response

Output representation of the response with error message and status.

JSON example
:   ```
    {
      "responseList": [
        {
          "status": true
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the operation fails. | Small, 64.0 | 64.0 |
| `status` | Boolean | Indicates whether the cache is cleared successfully (`true`) or not (`false`). | Small, 64.0 | 64.0 |
