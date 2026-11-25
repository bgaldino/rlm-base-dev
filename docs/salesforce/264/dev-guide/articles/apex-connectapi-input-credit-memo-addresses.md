---
page_id: apex-connectapi-input-credit-memo-addresses
title: ConnectApi.CreditMemoAddressesInputRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-addresses.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_credit_memo_addresses.htm
fetched_at: 2026-11-25
---

# ConnectApi.CreditMemoAddressesInputRequest

Input representation of the details of the billing and shipping addresses.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billingAddress` | [ConnectApi.BillingAddressRequest](./apex-connectapi-input-address.md) | Billing address for charge or adjustment line. | Optional | 62.0 |
| `shippingAddress` | [ConnectApi.BillingAddressRequest](./apex-connectapi-input-address.md) | Shipping address for charge or adjustment line. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-addresses.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
