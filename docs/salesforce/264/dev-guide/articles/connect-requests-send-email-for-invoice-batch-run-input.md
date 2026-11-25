---
page_id: connect-requests-send-email-for-invoice-batch-run-input
title: Send Email Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-send-email-for-invoice-batch-run-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_send_email_for_invoice_batch_run_input.htm
fetched_at: 2026-11-25
---

# Send Email Input

Input representation of the request to send an email for an invoice batch run.

## JSON Example

```
{
  "invoiceBatchRunId": "5IRLT000001SIJB4A4"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatchRunId` | String | ID of the invoice batch run record to send emails for the posted invoices of an invoice batch run. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-send-email-for-invoice-batch-run-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
