---
page_id: connect-responses-coupon-details
title: Promotion Coupon
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-coupon-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_coupon_details.htm
fetched_at: 2026-11-25
---

# Promotion Coupon

Output representation of the details of a coupon that’s eligible for the recommended promotion.

## JSON Example

```
{
  "coupon": {
    "couponCode": "COUPON_002",
    "endDateTime": null,
    "startDateTime": "2025-10-08T19:00:00.000Z",
    "status": "Active"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `couponCode` | String | Unique code of the coupon. | Big, 66.0 | 66.0 |
| `endDateTime` | String | End date and time of the coupon. | Big, 66.0 | 66.0 |
| `startDateTime` | String | Start date and time of the coupon. | Big, 66.0 | 66.0 |
| `status` | String | Status of the coupon. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-coupon-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
