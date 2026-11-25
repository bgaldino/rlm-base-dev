---
page_id: connect-requests-addresses-input
title: Addresses Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-addresses-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_addresses_input.htm
fetched_at: 2026-11-25
---

# Addresses Input

Input representation of the details of the addresses for calculating tax.

## JSON Example

```
{
  "addresses": {
    "billTo": {
      "street": "123 Main Street",
      "city": "Bainbridge Island",
      "state": "WA",
      "postalCode": "98110",
      "country": "US"
    },
    "soldTo": {
      "street": "123 Main Street",
      "city": "Bainbridge Island",
      "state": "WA",
      "postalCode": "98110",
      "country": "US"
    },
    "shipFrom": {
      "street": "123 Alaskan Way",
      "city": "Seattle",
      "state": "WA",
      "country": "US",
      "postalCode": "98101"
    },
    "shipTo": {
      "street": "123 Main street",
      "city": "Bainbridge Island",
      "state": "WA",
      "postalCode": "98110",
      "country": "US"
    }
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billTo` | [Address Input](./connect-requests-address-input.md) | Billing address of the item. | Optional | 62.0 |
| `shipFrom` | [Address Input](./connect-requests-address-input.md) | Address that the item is shipped from. | Optional | 62.0 |
| `shipTo` | [Address Input](./connect-requests-address-input.md) | Address that the item is shipped to. | Required | 62.0 |
| `soldTo` | [Address Input](./connect-requests-address-input.md) | Address of the entity that the item is sold to. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-addresses-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
