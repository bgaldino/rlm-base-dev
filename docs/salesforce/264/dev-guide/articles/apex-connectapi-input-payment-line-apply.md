---
page_id: apex-connectapi-input-payment-line-apply
title: ConnectApi.PaymentLineApplyRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-payment-line-apply.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_payment_line_apply.htm
fetched_at: 2026-11-25
---

# ConnectApi.PaymentLineApplyRequest

Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields, such as associated account and effective date.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount that’s applied. The amount must be less than the invoice line and payment balance. | Required | 64.0 |
| `applied​ToId` | String | ID of the invoice line that this payment is applied to. Specify the IDs for these records. | Required | 64.0 |
| `associated​AccountId` | String | ID of the associated account. | Optional | 64.0 |
| `comments` | String | Comments that you can add to the payment line application. | Optional | 64.0 |
| `effective​Date` | Datetime | Date from which the payment line application takes effect. | Optional | 64.0 |

applied​ToId values:

- Invoice

- Invoice Line

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-payment-line-apply.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
