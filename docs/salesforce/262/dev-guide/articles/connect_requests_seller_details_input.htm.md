---
page_id: connect_requests_seller_details_input.htm
title: Seller Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_seller_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Seller Details Input

Input representation of the seller details for tax calculation.

JSON example
:   ```
    {
      "code": "ADIDAS"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `code` | String | Seller code as specified in the tax engine. | Required | 62.0 |
