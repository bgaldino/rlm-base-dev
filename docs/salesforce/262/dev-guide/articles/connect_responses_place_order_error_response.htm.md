---
page_id: connect_responses_place_order_error_response.htm
title: Place Order Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_order_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Place Order Error Response

Output representation of the error response for the place order request.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code representing the type of error encountered during the place order create request. | Small, 60.0 | 60.0 |
| `message` | String | Message stating the reason for the error, if any. | Small, 60.0 | 60.0 |
| `reference​Id` | String | Reference ID associated with the specific error instance for tracking and reference purposes. | Small, 60.0 | 60.0 |
