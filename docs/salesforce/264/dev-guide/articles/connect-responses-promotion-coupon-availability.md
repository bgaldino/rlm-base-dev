---
page_id: connect-responses-promotion-coupon-availability
title: Promotion Coupon Availability
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-coupon-availability.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_promotion_coupon_availability.htm
fetched_at: 2026-11-25
---

# Promotion Coupon Availability

Output representation of the details of the coupon that’s eligible for the promotion. Additionally, this representation specifies the reason for any coupon ineligibility.

## JSON Example

```
{
  "couponDetails": {
    "coupon": {
      "couponCode": "COUPON_002",
      "endDateTime": null,
      "startDateTime": "2025-10-08T19:00:00.000Z",
      "status": "Active"
    },
    "couponAvailabilityMessage": null
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `coupon` | [Promotion Coupon](./connect-responses-coupon-details.md)[] | Coupon that’s eligible for the customers’ cart. | Big, 66.0 | 66.0 |
| `couponAvailability​Message` | String | Specifies the reason for coupon ineligibility for the promotion. Valid values are `MultipleActiveCoupons`, `NoActiveCoupons`, or `SingleActiveCouponLimitReached`. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-coupon-availability.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
