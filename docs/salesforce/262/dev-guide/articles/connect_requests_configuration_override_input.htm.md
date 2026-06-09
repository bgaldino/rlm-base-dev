---
page_id: connect_requests_configuration_override_input.htm
title: Configuration Override Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configuration_override_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Configuration Override Input

Input representation of the details to override for a Pricing API
configuration.

JSON example
:   ```
        "configurationOverrides": {
             "skipWaterfall": true,
             "useSessionScopedContext": true,
             "persistContext": true,
             "referenceKey": "referenceKey-12345",
             "displayContext" : false,
             "taggedData": false,
             "isHighVolumeLineItems": false
        }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `discovery​Procedure` | String | Name of the discovery procedure to use to fetch the details of assets. | Optional | 61.0 |
    | `display​Context` | Boolean | Indicates whether the context structure for pricing must be displayed (`true`) or not (`false`). | Optional | 61.0 |
    | `isHighVolume​LineItems` | Boolean | Indicates whether the pricing API returns pricing details for more than 100 line items (`true`) or not (`false`). | Optional | 63.0 |
    | `persist​Context` | Boolean | Indicates whether the context must be persisted as per the mapping (`true`) or not (`false`). If set to `true`, the user must have edit access to all sObject fields used in the context mapping. | Optional | 60.0 |
    | `reference​Key` | String | Reference ID that a consuming workstream provides in the API to search for specific logs in the Pricing Operations Console. | Optional | 63.0 |
    | `skip​Discovery` | Boolean | Indicates whether the discovery procedure must be skipped (`true`) or not (`false`). | Optional | 61.0 |
    | `skip​Waterfall` | Boolean | Indicates whether the price waterfall must be skipped in the output response (`true`) or not (`false`). | Optional | 60.0 |
    | `tagged​Data` | Boolean | Indicates whether the JSON data string can specify tags in the input instead of attributes (`true`) or not (`false`). | Optional | 60.0 |
    | `useSession​Scoped​Context` | Boolean | Indicates whether a session scoped context must be created (`true`) or request scoped context (`false`). The default is `false`. | Optional | 60.0 |
