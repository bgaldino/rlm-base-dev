---
page_id: apex-connectapi-input-invoice
title: ConnectApi.InvoiceInputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-invoice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_invoice.htm
fetched_at: 2026-11-25
---

# ConnectApi.InvoiceInputRepresentation

Input representation of the details of the billing schedule.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | `ConnectApi.InvoiceAction` | Type of invoice to be created. | Required | 62.0 |
| `billing​ScheduleIds` | List<`String`> | List of billing schedule IDs that’s used to create the invoices. You can specify a maximum of 200 billing schedules. | Required | 62.0 |
| `correlation​Id` | String | Property that’s tagged against the published `InvoiceProcessedEvent` event, if specified. | Optional | 62.0 |
| `invoice​Date` | String | Stamping date of the invoice in ISO 8601 format. | Required | 62.0 |
| `target​Date` | String | Date in ISO 8601 format used to decide the billing periods that are included to create invoices. | Required | 62.0 |

action values:

- `Draft`

- `Posted`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-invoice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
