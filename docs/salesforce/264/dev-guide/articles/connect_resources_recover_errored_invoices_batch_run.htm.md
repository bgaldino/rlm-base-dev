---
page_id: connect_resources_recover_errored_invoices_batch_run.htm
title: Invoice Run Recovery (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_recover_errored_invoices_batch_run.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Invoice Run Recovery (POST)

Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status.

## Special Access Rules

To use this API, you need the Invoice Scheduler API permission set.

## Resource

```
/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/recover
```

The invoiceBatchRunId parameter is the ID of the failed invoice batch run record whose details you want to retrieve.

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/5IRxx0000004TwGGAU/actions/recover
```

## Available Version

62.0

## HTTP Methods

POST

## Response Body for POST

[Invoice Batch Run Recovery](./connect_responses_invoice_batch_run_recovery_output.htm.md "Output representation of the details of the invoice batch run recovery record.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_recover_errored_invoices_batch_run.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
