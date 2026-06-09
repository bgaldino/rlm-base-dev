---
page_id: connect_requests_p_b_e_derived_pricing_input.htm
title: PBE Derived Pricing Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_p_b_e_derived_pricing_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# PBE Derived Pricing Input

Input representation of the request to get the source product for the Price Book Entry
(PBE) derived pricing.

JSON example
:   ```
    {
    "productId":"01txx0000006i2SAAQ",
    "pricebookEntryId":"01uxx0000008yYcAAI",
    "effectiveFrom":"2020-01-01T22:53:20.000Z",
    "effectiveTo":"2021-01-01T22:53:20.000Z"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `effective​From` | String | Date from when the price book entry is effective. | Required | 61.0 |
    | `effective​To` | String | Date until when the price book entry is effective. | Required | 61.0 |
    | `pricebook​EntryId` | String | ID of the price book entry. | Required | 61.0 |
    | `product​Id` | String | ID of the price book. | Required | 61.0 |
