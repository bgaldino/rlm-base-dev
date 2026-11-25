---
page_id: sforce-api-objects-invoiceerrordetailevent
title: InvoiceErrorDetailEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoiceerrordetailevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: sforce-api-objects-invoiceprocessedevent
legacy_page_id: sforce_api_objects_invoiceerrordetailevent.htm
fetched_at: 2026-11-25
---

# InvoiceErrorDetailEvent

Represents information about the errors that occurred during the processing of a `/commerce/billing/invoices` request. This object is included in an `InvoiceProcessedEvent` platform event message. You can’t subscribe to `InvoiceProcessedEvent` platform event directly. This object is available in API version 62.0 and later.

## Supported Calls

`describeSObjects()`

## Special Access Rules

This object is available when Billing is enabled.

## Fields

### ErrorCode

- **Type**: string

- **Properties**: None

- **Description**: Reference code for the type of error that occurred.

### ErrorMessage

- **Type**: string

- **Properties**: None

- **Description**: Information about the error that occurred during processing.

### ErrorSourceId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the record where the error occurred. This record can be an invoice or a billing schedule.

This field is a polymorphic relationship field.

- **Relationship Name**: ErrorSource

- **Refers To**: BillingSchedule, Invoice

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoiceerrordetailevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
