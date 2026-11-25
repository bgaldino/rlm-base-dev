---
page_id: connect-resources-send-email-for-invoice-batch-run
title: Send Emails for Posted Invoices (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-send-email-for-invoice-batch-run.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_send_email_for_invoice_batch_run.htm
fetched_at: 2026-11-25
---

# Send Emails for Posted Invoices (POST)

Send emails for the posted invoices of a specified invoice batch run ID.

Each email includes a custom message template in the email body and an attachment of the Invoice Document PDF. The email template is based on the user preferences defined on the Billing Profile, Legal Entity, or Billing Settings page.

## Special Access Rules

Enable the **Configure Email Delivery Settings** toggle from the Billing Settings page from Setup.

## Resource

```
/commerce/invoicing/invoice-batch-runs/actions/send-email
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/actions/send-email
```

## Available Version

65.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "invoiceBatchRunId": "5IRLT000001SIJB4A4"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatchRunId` | String | ID of the invoice batch run record to send emails for the posted invoices of an invoice batch run. | Required | 65.0 |

## Response Body for POST

[Send Email Response](./connect-responses-send-email-for-invoice-batch-run-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-send-email-for-invoice-batch-run.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
