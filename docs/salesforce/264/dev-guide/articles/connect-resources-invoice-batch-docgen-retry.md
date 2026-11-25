---
page_id: connect-resources-invoice-batch-docgen-retry
title: Batch Invoices Document Generation Retry (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-invoice-batch-docgen-retry.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_invoice_batch_docgen_retry.htm
fetched_at: 2026-11-25
---

# Batch Invoices Document Generation Retry (POST)

Asynchronously regenerate PDF documents for the invoices that are in the `Draft` or `Posted` status and failed in an earlier invoice batch run.

## Special Access Rules

This API is available with Revenue Cloud Billing. To use this API, enable Document Generation for Billing. Additionally, you need either the Billing Operations User permission set or the Billing Admin permission set, along with the Docgen Designer permission set and Docgen Designer Standard User permission set.

## Resource

```
/commerce/billing/invoices/invoice-batch-docgen/{invoiceBatchRunId}/actions/{actionName}
```

- The *invoiceBatchRunId* parameter is the ID of the invoice batch run record that created the `Draft` or `Posted` invoices.

- The *actionName* parameter is the name of the action you want to perform on the specified invoice batch run record. In this case, the action is to retry generating the `Draft` or `Posted` invoices that failed earlier.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/billing/invoices/invoice-batch-docgen/{5IRxx0000004GSmGAM}/actions/{retry}
```

## Available Version

63.0

## HTTP Methods

POST

## Response Body for POST

[Batch Invoice Document Generation](./connect-responses-batch-invoice-doc-gen-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-invoice-batch-docgen-retry.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
