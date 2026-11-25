---
page_id: connect-resources-get-billing-arrangement
title: Billing Arrangement (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-billing-arrangement.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_get_billing_arrangement.htm
fetched_at: 2026-11-25
---

# Billing Arrangement (GET)

Retrieve a billing arrangement and its associated billing arrangement lines.

This API fetches billing information, including the split percentage allocation for accounts, the remainder percentage, and whether adjustments are applied to the owning account.

## Resource

```
/revenue/billing/billing-arrangement/{billingArrangementId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/billing/billing-arrangement//revenue/billing/billing-arrangement/{1bdxx000000004rAAA}
```

## Available Version

66.0

## HTTP Methods

GET

## Request Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​ArrangementId` | String | Unique ID of the billing arrangement to retrieve. | Required | 66.0 |

## Response Body for GET

[Billing Arrangement](./connect-responses-billing-arrangement-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-billing-arrangement.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
