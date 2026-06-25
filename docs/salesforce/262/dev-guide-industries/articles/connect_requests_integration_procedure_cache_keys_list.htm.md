---
page_id: connect_requests_integration_procedure_cache_keys_list.htm
title: Integration Procedure Cache Keys
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_keys_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-06-25
---

# Integration Procedure Cache Keys

Input representation of the cache keys to clear the execution cache.

JSON example
:   ```
    {
        "cacheKeys": [
          "IP06535636"
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `cacheKeys` | String[] | List of cache keys to clear the cache for. | Optional | 64.0 |
