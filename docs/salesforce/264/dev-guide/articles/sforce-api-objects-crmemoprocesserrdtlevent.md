---
page_id: sforce-api-objects-crmemoprocesserrdtlevent
title: CrMemoProcessErrDtlEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-crmemoprocesserrdtlevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: sforce-api-objects-creditinvoiceprocessedevent
legacy_page_id: sforce_api_objects_crmemoprocesserrdtlevent.htm
fetched_at: 2026-11-25
---

# CrMemoProcessErrDtlEvent

Represents the information about errors that occurred while creating or applying a credit memo as part of a request. This object is included in a `CreditInvoiceProcessedEvent`, `CreditMemoProcessedEvent,` `NegInvcLineProcessedEvent`, or `VoidInvoiceProcessedEvent` platform event message. You can’t subscribe to `CrMemoProcessErrDtlEvent` platform event directly. This object is available in API version 62.0 and later.

## Supported Calls

`describeSObjects()`

## Special Access Rules

This object is available when Billing is enabled.

## Fields

### ErrorCode

- **Type**: string

- **Properties**: Nillable

- **Description**: Reference code for the type of error that occurred.

### ErrorMessage

- **Type**: string

- **Properties**: Nillable

- **Description**: Information about the error that occurred during processing.

### ErrorSourceId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the record on which the error occurred during the credit memo creation process and the application process.

This field is a polymorphic relationship field.

- **Relationship Name**: ErrorSource

- **Refers To**: CreditMemo, CreditMemoLine, Invoice, InvoiceLine

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-crmemoprocesserrdtlevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
