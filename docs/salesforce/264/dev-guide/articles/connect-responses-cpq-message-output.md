---
page_id: connect-responses-cpq-message-output
title: CPQ Message
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-cpq-message-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_cpq_message_output.htm
fetched_at: 2026-11-25
---

# CPQ Message

Output representation of the API messages.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code specifying the type of message. Valid value is `CartValidationError`. | Small, 60.0 | 60.0 |
| `detail` | String | Required details other than the message text. | Small, 60.0 | 60.0 |
| `message` | String | Text of the API message. | Small, 60.0 | 60.0 |
| `severity` | String | Severity of the API message. Valid values are `Error`, `Info`, or `Warning`. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-cpq-message-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
