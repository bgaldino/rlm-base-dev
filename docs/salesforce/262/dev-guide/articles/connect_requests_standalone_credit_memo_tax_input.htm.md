---
page_id: connect_requests_standalone_credit_memo_tax_input.htm
title: Standalone Credit Memo Tax Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_standalone_credit_memo_tax_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Standalone Credit Memo Tax Input

Input representation of the details of the tax request.

JSON example
:   ```
    [
      {
        "taxAmount": 200,
        "taxName": "Federal Tax",
        "taxRate": 1
      },
      {
        "taxAmount": 500,
        "taxName": "State Tax",
        "taxRate": 1
      }
    ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `taxAmount` | Double | Amount of tax to be applied. | Required | 62.0 |
    | `taxCode` | String | Tax code to be used to create the tax line. | Optional | 62.0 |
    | `taxName` | String | Name of tax to be applied. | Optional | 62.0 |
    | `taxRate` | Double | Tax rate to be used to create the tax line. | Optional | 62.0 |
