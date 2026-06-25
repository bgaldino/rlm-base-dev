---
page_id: connect_resources_integration_procedure_clear_cache.htm
title: Integration Procedure Clear Cache (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_integration_procedure_clear_cache.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_resources.htm
fetched_at: 2026-06-25
---

# Integration Procedure Clear Cache (POST)

Clear the execution cache for the specified integration procedures.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

When using the Integration Procedure (IP) Connect API, HTTP
callouts cannot be executed in the same transaction. This is because these APIs perform an
implicit DML operation through the underlying Connect API framework. If a callout is
required, it must be executed in a separate transaction, for example by using an
asynchronous mechanism such as @future.

Resource
:   ```
    /connect/omni-global/integration-procedure/actions/clear-cache
    ```

Available version
:   64.0

HTTP methods
:   POST

Request body for POST
:   JSON example
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

Response body for POST
:   [Integration Procedure
    Cache Details](./connect_responses_integration_procedure_cache_output.htm.md "Output representation of the cache that are cleared for the specified integration procedures.")
