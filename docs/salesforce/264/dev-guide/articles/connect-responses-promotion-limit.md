---
page_id: connect-responses-promotion-limit
title: Promotion Limit
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-limit.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_promotion_limit.htm
fetched_at: 2026-11-25
---

# Promotion Limit

Output representation of the details of the promotion limit of an eligible promotion.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `limitCurrent​Attainment` | Double | Current attainment of the promotion’s limit value. | Big, 66.0 | 66.0 |
| `limitTarget` | Double | Value beyond which the promotion can’t be applied to customer carts. | Big, 66.0 | 66.0 |
| `limitType` | String | Limit type for the promotion. Valid values are `CartItemCount`—Specifes the limit type that represents the maximum number of cart items the promotion can applied for or `OrderCount`—Specifies the limit type that represents the maximum number of carts the promotion can applied for. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-limit.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
