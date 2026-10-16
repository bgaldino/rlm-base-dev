---
page_id: connect_requests_integration_procedure_cache_input.htm
title: Integration Procedure Clear Cache Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Clear Cache Input

Input representation of the details to clear the execution cache of the integration
    procedures.

**JSON example**

          
: This is a sample example to clear the cache of an integration procedure by using the
            key that's associated with the integration procedure and cache storage type.

          
: 
            

```
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

          

          
: This is a sample example to clear the cache of an integration procedure by using the
            cache keys and cache storage type.

: 

```
{
  "cacheKeys": {
    "cacheKeys": [
      "IP06535636"
    ]
  },
  "cacheStorageType": "Metadata"
}
```

**Properties**

: 

- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheKeys` | [Integration Procedure Cache Keys](./connect_requests_integration_procedure_cache_keys_list.htm.md) | List of cache keys to clear the cache for. Cache keys are used to identify the cached data. | Optional | 64.0 |
| `cacheStorageType` | String | Storage type that's used for caching the data. Valid values are: `All`—Includes all cache types, such as metadata, session, and org-level caches. `Metadata`—Cache is used for configuration-related data such as schemas or field mappings. `Org`—Cache is shared across the entire organization. `Session`—Cache is stored in the current user session. | Required | 64.0 |
| `iPInput` | [Integration Procedure Details](./connect_requests_integration_procedure_cache_input_data.htm.md)[] | List of integration procedures to clear the cache for. | Optional | 64.0 |
