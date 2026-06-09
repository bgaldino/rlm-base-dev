---
page_id: connect_responses_coupon_details.htm
title: Promotion Coupon
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_coupon_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Promotion Coupon

Output representation of the details of a coupon that's eligible for the recommended
promotion.

JSON example
:   ```
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
