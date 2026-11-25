---
page_id: apex-connectapi-input-refund-line-apply
title: ConnectApi.RefundLineApplyRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-refund-line-apply.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_refund_line_apply.htm
fetched_at: 2026-11-25
---

# ConnectApi.RefundLineApplyRequest

Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount to refund. | Required | 64.0 |
| `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
| `comments` | String | Additional details of the refund request. | Optional | 64.0 |
| `effectiveDate` | Datetime | Date from when the refund is in effect. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-refund-line-apply.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
