---
page_id: connect-responses-addresses-output
title: Addresses
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-addresses-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_addresses_output.htm
fetched_at: 2026-11-25
---

# Addresses

Output representation of the details of the addresses that are used for calculating tax.

## JSON Example

```
{
  "addresses": {
    "shipFrom": {
      "locationCode": "67890"
    },
    "shipTo": {
      "locationCode": "12345"
    },
    "soldTo": {
      "locationCode": "12345"
    }
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `shipFrom` | [Address](./connect-responses-address-output.md) | Address that the item is shipped from. | Big, 62.0 | 62.0 |
| `shipTo` | [Address](./connect-responses-address-output.md) | Address that the item is shipped to. | Big, 62.0 | 62.0 |
| `soldTo` | [Address](./connect-responses-address-output.md) | Address that the item is sold to. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-addresses-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
