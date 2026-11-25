---
page_id: connect-responses-api-status-output
title: API Status
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-status-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_api_status_output.htm
fetched_at: 2026-11-25
---

# API Status

Output representation of the API status.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `messages` | [CPQ Message](./connect-responses-cpq-message-output.md)[] | Status messages of the API execution. | Small, 60.0 | 60.0 |
| `status​Code` | String | Status code of the API execution. | Small, 60.0 | 60.0 |
| `status​Message` | String | Display label for the API status. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-status-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
