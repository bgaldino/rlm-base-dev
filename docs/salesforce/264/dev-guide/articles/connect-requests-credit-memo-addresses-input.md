---
page_id: connect-requests-credit-memo-addresses-input
title: Credit Memo Addresses Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-memo-addresses-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_credit_memo_addresses_input.htm
fetched_at: 2026-11-25
---

# Credit Memo Addresses Input

Input representation of the details of the billing and shipping addresses.

## JSON Example

```
{
  "billingAddress": {
    "street": "1 Market St #300",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postalCode": "94105",
    "latitude": "37.789901",
    "longitude": "-122.396923"
  },
  "shippingAddress": {
    "street": "415 Mission St",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postalCode": "94105",
    "latitude": "37.789901",
    "longitude": "-122.396923"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Address` | [Address Input](./connect-requests-address-input.md)[] | Billing address for charge or adjustment line. | Optional | 62.0 |
| `shipping​Address` | [Address Input](./connect-requests-address-input.md)[] | Shipping address for charge or adjustment line. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-memo-addresses-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
