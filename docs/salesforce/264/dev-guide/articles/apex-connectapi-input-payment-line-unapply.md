---
page_id: apex-connectapi-input-payment-line-unapply
title: ConnectApi.PaymentLineUnapplyRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-payment-line-unapply.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_payment_line_unapply.htm
fetched_at: 2026-11-25
---

# ConnectApi.PaymentLineUnapplyRequest

Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `comments` | String | Comments that you can add when you revert a payment line application. | Optional | 64.0 |
| `effective​Date` | Datetime | Date from when the reversal of the payment line application is in effect. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-payment-line-unapply.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
