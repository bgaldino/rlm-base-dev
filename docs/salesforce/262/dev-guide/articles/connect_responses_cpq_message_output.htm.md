---
page_id: connect_responses_cpq_message_output.htm
title: CPQ Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_cpq_message_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# CPQ Message

Output representation of the API messages.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code specifying the type of message. Valid value is `CartValidationError`. | Small, 60.0 | 60.0 |
| `detail` | String | Required details other than the message text. | Small, 60.0 | 60.0 |
| `message` | String | Text of the API message. | Small, 60.0 | 60.0 |
| `severity` | String | Severity of the API message. Valid values are:  - `Error` - `Info` - `Warning` | Small, 60.0 | 60.0 |
