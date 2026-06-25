---
page_id: connect_requests_datamapper_cache_input_param.htm
title: Data Mapper Clear Cache Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_datamapper_cache_input_param.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-06-25
---

# Data Mapper Clear Cache Input

Input representation of the details to clear the cache of the data mappers.

JSON example
:   This is a sample example to clear the execution cache by using only the name of the
    data mapper.
:   ```
    {
      "cacheStorageType": "Metadata",
      "dataMapperList": {
        "dataMappers": [
          {
            "dataMapperName": "DRWithLoad"
          }
        ]
      }
    }
    ```
:   This is a sample example to clear the execution cache by using the name of the data
    mapper along with additional inputs.
:   ```
    {
      "cacheStorageType": "Session",
      "dataMapperList": {
        "dataMappers": [
          {
            "dataMapperName": "DRWithLoad",
            "input": {
              "Name": "Get Account Details"
            }
          }
        ]
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `cacheStorageType` | String | Storage type that's used for caching the data. Valid values are:  - `Session`—Cache is stored in   the current user session. - `Org`—Cache is shared across   the entire organization. - `All`—Refers to both session   and org-level cache. | Required | 64.0 |
    | `dataMapperList` | [Data Mapper Details](./connect_requests_data_mapper_details.htm.md "Input representation of the data mapper details to clear the cache for.")[] | List of data mappers to clear the cache for. | Required | 64.0 |
