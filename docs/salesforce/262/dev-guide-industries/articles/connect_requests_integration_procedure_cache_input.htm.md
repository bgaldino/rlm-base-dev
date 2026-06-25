---
page_id: connect_requests_integration_procedure_cache_input.htm
title: Integration Procedure Clear Cache Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-06-25
---

# Integration Procedure Clear Cache Input

Input representation of the details to clear the execution cache of the integration
procedures.

JSON example
:   This is a sample example to clear the cache of an integration procedure by using the
    key that's associated with the integration procedure and cache storage type.
:   ```
    {
      "cacheStorageType": "Metadata",
      "ipInput": {
        "inputs": [
          {
            "ipkey": "Account_GetAccountDetails"
          }
        ]
      }
    }
    ```
:   This is a sample example to clear the cache of an integration procedure by using the
    cache keys and cache storage type.
:   ```
    {
      "cacheKeys": {
        "cacheKeys": [
          "IP06535636"
        ]
      },
      "cacheStorageType": "Metadata"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `cacheKeys` | [Integration Procedure Cache Keys](./connect_requests_integration_procedure_cache_keys_list.htm.md "Input representation of the cache keys to clear the execution cache.") | List of cache keys to clear the cache for. Cache keys are used to identify the cached data. | Optional | 64.0 |
    | `cacheStorageType` | String | Storage type that's used for caching the data. Valid values are:  - `All`—Includes all cache   types, such as metadata, session, and org-level caches. - `Metadata`—Cache is used for   configuration-related data such as schemas or field mappings. - `Org`—Cache is shared across   the entire organization. - `Session`—Cache is stored in   the current user session. | Required | 64.0 |
    | `iPInput` | [Integration Procedure Details](./connect_requests_integration_procedure_cache_input_data.htm.md "Input representation of the details of the integration procedures to clear the cache for.")[] | List of integration procedures to clear the cache for. | Optional | 64.0 |
