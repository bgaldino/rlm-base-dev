---
page_id: connect-resources-recover-errored-invoices-batch-run
title: Invoice Run Recovery (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-recover-errored-invoices-batch-run.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_recover_errored_invoices_batch_run.htm
fetched_at: 2026-11-25
---

# Invoice Run Recovery (POST)

Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status.

## Special Access Rules

To use this API, you need the Invoice Scheduler API permission set.

## Resource

```
/commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/recover
```

The *invoiceBatchRunId* parameter is the ID of the failed invoice batch run record whose details you want to retrieve.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/{5IRxx0000004TwGGAU}/actions/recover
```

## Available Version

62.0

## HTTP Methods

POST

## Response Body for POST

[Invoice Batch Run Recovery](./connect-responses-invoice-batch-run-recovery-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-recover-errored-invoices-batch-run.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
