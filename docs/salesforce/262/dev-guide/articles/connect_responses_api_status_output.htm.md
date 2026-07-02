---
page_id: connect_responses_api_status_output.htm
title: API Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_api_status_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# API Status

Output representation of the API status.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `messages` | [CPQ Message](./connect_responses_cpq_message_output.htm.md "Output representation of the API messages.")[] | Status messages of the API execution. | Small, 60.0 | 60.0 |
| `status​Code` | String | Status code of the API execution. | Small, 60.0 | 60.0 |
| `status​Message` | String | Display label for the API status. | Small, 60.0 | 60.0 |
