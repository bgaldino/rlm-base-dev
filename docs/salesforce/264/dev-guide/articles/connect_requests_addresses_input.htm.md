---
page_id: connect_requests_addresses_input.htm
title: Addresses Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_addresses_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Addresses Input

Input representation of the details of the addresses for calculating tax.

**JSON example**

: 

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

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billTo` | [Address Input](./connect_requests_address_input.htm.md) | Billing address of the item. | Optional | 62.0 |
| `shipFrom` | [Address Input](./connect_requests_address_input.htm.md) | Address that the item is shipped from. | Optional | 62.0 |
| `shipTo` | [Address Input](./connect_requests_address_input.htm.md) | Address that the item is shipped to. | Required | 62.0 |
| `soldTo` | [Address Input](./connect_requests_address_input.htm.md) | Address of the entity that the item is sold to. | Optional | 62.0 |
