---
page_id: connect_responses_addresses_output.htm
title: Addresses
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_addresses_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
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
| `shipFrom` | [Address](./connect_responses_address_output.htm.md "Output representation of the location code associated with an address.") | Address that the item is shipped from. | Big, 62.0 | 62.0 |
| `shipTo` | [Address](./connect_responses_address_output.htm.md "Output representation of the location code associated with an address.") | Address that the item is shipped to. | Big, 62.0 | 62.0 |
| `soldTo` | [Address](./connect_responses_address_output.htm.md "Output representation of the location code associated with an address.") | Address that the item is sold to. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_addresses_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
