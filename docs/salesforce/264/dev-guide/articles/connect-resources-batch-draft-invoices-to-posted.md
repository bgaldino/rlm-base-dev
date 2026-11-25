---
page_id: connect-resources-batch-draft-invoices-to-posted
title: Batch Invoices Draft to Posted Status (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-batch-draft-invoices-to-posted.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_batch_draft_invoices_to_posted.htm
fetched_at: 2026-11-25
---

# Batch Invoices Draft to Posted Status (POST)

Update a batch of invoices from `Draft` to `Posted` status for a credit memo application.

## Special Access Rules

To use this API, you need the Billing Operations User permission set.

## Resource

```
/commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/draft-to-posted
```

This API posts the draft invoices and changes the status of the invoices from `Draft` to `Posted`.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/{5IRNZ0000000cA94AI}/actions/draft-to-posted
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoice​Batch​RunId` | String | ID of the invoice batch run record that creates the draft invoices. | Required | 62.0 |

## Response Body for POST

[Invoice Batch Draft To Posted](./connect-responses-invoice-batch-draft-to-posted-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-batch-draft-invoices-to-posted.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
