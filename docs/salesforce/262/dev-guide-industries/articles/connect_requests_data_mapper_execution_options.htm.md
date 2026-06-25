---
page_id: connect_requests_data_mapper_execution_options.htm
title: Data Mapper Execution Options
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execution_options.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-06-25
---

# Data Mapper Execution Options

Input representation of the optional parameters for the data mapper
execution.

JSON example
:   ```
    {
      "options": {
        "ignoreCache": false,
        "locale": "en-US"
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `ignoreCache` | Boolean | Indicates whether to ignore the cache during the data mapper execution (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `ignore​MetadataCache` | Boolean | Indicates whether to ignore the metadata cache during the data mapper execution (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `ignoreMetadata​Permissions` | Boolean | Indicates whether to ignore the metadata permission during the data mapper execution (`true`) or elevate the metadata permission (`false`). The default value is `false`. | Optional | 64.0 |
    | `locale` | String | Locale that's applied during the data mapper execution. | Optional | 64.0 |
    | `resetCache` | Boolean | Indicates whether to reset the cache during the data mapper execution (`true`) or not (`false`). If set to `true`, data is fetched from the database instead of cache.  The default value is `false`. | Optional | 64.0 |
    | `shouldIgnore​Commit` | Boolean | Indicates whether to skip committing the transaction data to database (`true`)or not (`false`). The default value is `true`. | Optional | 64.0 |
    | `shouldSend​LegacyResponse` | Boolean | Indicates whether response is displayed in the legacy Apex object format (`true`) or in generic format (`false`). The default value is `false`. | Optional | 64.0 |
    | `withoutSharing` | Boolean | Indicates whether the Data Mapper must ignore the user sharing rules while executing the data (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
