---
page_id: apex_connectapi_input_credit_memo_addresses.htm
title: ConnectApi.CreditMemoAddressesInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_addresses.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.CreditMemoAddressesInputRequest

Input representation of the details of the billing and shipping addresses.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billingAddress` | [ConnectApi.BillingAddressRequest](./apex_connectapi_input_address.htm.md) | Billing address for charge or adjustment line. | Optional | 62.0 |
| `shippingAddress` | [ConnectApi.BillingAddressRequest](./apex_connectapi_input_address.htm.md) | Shipping address for charge or adjustment line. | Optional | 62.0 |
