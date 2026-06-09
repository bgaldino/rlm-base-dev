---
page_id: connect_requests_pricing_request.htm
title: Pricing Request Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_request.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Pricing Request Input

Input representation of a pricing request.

JSON example
:   ```
    {
        "configurationOverrides": {
           "skipWaterfall": true,
           "useSessionScopedContext": true,
           "persistContext": true,
           "taggedData": false
        }
        "procedureName": "ES1"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `configuration​Overrides` | [Configuration Override Input](./connect_requests_configuration_override_input.htm.md "Input representation of the details to override for a Pricing API configuration.") | Parameters to override pricing configuration. | Optional | 60.0 |
    | `procedure​Name` | String | Name of the pricing procedure. | Optional | 60.0 |
