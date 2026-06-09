---
page_id: connect_responses_place_supplemental_transaction_error_response.htm
title: Supplemental Transaction Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_supplemental_transaction_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Supplemental Transaction Error Response

Output representation of the error details associated with the Place Supplemental
Transaction API.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Small, 64.0 | 64.0 |
| `message` | String | Message stating the reason for error, if any. | Small, 64.0 | 64.0 |
| `referenceId` | String | Unique ID that’s associated with the specific error for tracking and reference purposes. | Small, 64.0 | 64.0 |
