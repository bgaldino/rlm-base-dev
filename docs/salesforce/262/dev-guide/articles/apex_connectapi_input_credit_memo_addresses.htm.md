---
page_id: apex_connectapi_input_credit_memo_addresses.htm
title: ConnectApi.CreditMemoAddressesInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_addresses.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditMemoAddressesInputRequest

Input representation of the details of the billing and shipping addresses.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billingAddress` | [ConnectApi.BillingAddressRequest](./apex_connectapi_input_address.htm.md "Input representation of the details of an address.") | Billing address for charge or adjustment line. | Optional | 62.0 |
| `shippingAddress` | [ConnectApi.BillingAddressRequest](./apex_connectapi_input_address.htm.md "Input representation of the details of an address.") | Shipping address for charge or adjustment line. | Optional | 62.0 |
