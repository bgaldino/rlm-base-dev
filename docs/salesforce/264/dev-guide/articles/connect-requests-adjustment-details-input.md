---
page_id: connect-requests-adjustment-details-input
title: Adjustment Details Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-adjustment-details-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_adjustment_details_input.htm
fetched_at: 2026-11-25
---

# Adjustment Details Input

Input representation of the adjustment details.

## JSON Example

```
   "pricingElement": {
     "adjustments": [{
     "AdjustmentValue": "15.00",
     "AdjustmentType": "Percentage"
  }],
   "description": null,
   "elementType": "VolumeDiscount",
   "name": "Volume Discount"
 }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `adjustments` | Map<String, Object>[] | Details of the pricing element. | Optional | 60.0 |
| `description` | String | Description of the pricing element. | Optional | 60.0 |
| `elementType` | String | Type of the pricing element. | Optional | 60.0 |
| `name` | String | Name of the pricing element. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-adjustment-details-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
