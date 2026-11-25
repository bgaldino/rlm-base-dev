---
page_id: connect-requests-p-b-e-derived-pricing-input
title: PBE Derived Pricing Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-p-b-e-derived-pricing-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_p_b_e_derived_pricing_input.htm
fetched_at: 2026-11-25
---

# PBE Derived Pricing Input

Input representation of the request to get the source product for the Price Book Entry (PBE) derived pricing.

## JSON Example

```
{
"productId":"01txx0000006i2SAAQ",
"pricebookEntryId":"01uxx0000008yYcAAI",
"effectiveFrom":"2020-01-01T22:53:20.000Z",
"effectiveTo":"2021-01-01T22:53:20.000Z"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effective​From` | String | Date from when the price book entry is effective. | Required | 61.0 |
| `effective​To` | String | Date until when the price book entry is effective. | Required | 61.0 |
| `pricebook​EntryId` | String | ID of the price book entry. | Required | 61.0 |
| `product​Id` | String | ID of the price book. | Required | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-p-b-e-derived-pricing-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
