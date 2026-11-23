---
page_id: connect_requests_address_input.htm
title: Address Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_address_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Address Input

Input representation of the details of an address.

## JSON Example

**JSON Example**

```
  "billingAddress": {
    "street": "1 Market St #300",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postalCode": "94105",
    "latitude": "37.789901",
    "longitude": "-122.396923"
  }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `city` | String | Address city. | Optional | 62.0 |
| `country` | String | Address country. | Optional | 62.0 |
| `latitude` | Double | Latitude for the address. | Optional | 62.0 |
| `locationCode` | String | Location code for the address. | Optional | 62.0 |
| `longitude` | Double | Longitude for the address. | Optional | 62.0 |
| `postalCode` | String | Postal code for the address. | Optional | 62.0 |
| `state` | String | Address state. | Optional | 62.0 |
| `street` | String | Address street. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_address_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
