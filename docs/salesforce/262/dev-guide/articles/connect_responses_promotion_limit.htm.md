---
page_id: connect_responses_promotion_limit.htm
title: Promotion Limit
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_promotion_limit.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Promotion Limit

Output representation of the details of the promotion limit of an eligible
promotion.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `limitCurrent​Attainment` | Double | Current attainment of the promotion's limit value. | Big, 66.0 | 66.0 |
| `limitTarget` | Double | Value beyond which the promotion can't be applied to customer carts. | Big, 66.0 | 66.0 |
| `limitType` | String | Limit type for the promotion. Valid values are:   - `CartItemCount`—Specifes the limit type that   represents the maximum number of cart items the promotion can applied for. - `OrderCount`—Specifies the limit type that   represents the maximum number of carts the promotion can applied for. | Big, 66.0 | 66.0 |
