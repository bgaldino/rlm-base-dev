---
page_id: connect_requests_customer_details_input.htm
title: Customer Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_customer_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Customer Details Input

Input representation of the customer details for tax calculation.

JSON example
:   ```
    {
        "accountId": "001R000000000zSMAQ"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `accountId` | String | Salesforce account ID of the customer. | Optional | 62.0 |
