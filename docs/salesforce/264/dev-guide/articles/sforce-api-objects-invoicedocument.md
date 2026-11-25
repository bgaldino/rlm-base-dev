---
page_id: sforce-api-objects-invoicedocument
title: InvoiceDocument
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoicedocument.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_invoicedocument.htm
fetched_at: 2026-11-25
---

# InvoiceDocument

Represents the PDF document generated for an invoice. This object is available in API version 63.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need Revenue Cloud Billing license, and the Billing Admin permission set or the Billing Operations User permission set to access this object.

## Fields

### ContentDocumentId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The ID of the generated PDF document.

This field is a relationship field.

- **Relationship Name**: ContentDocument

- **Refers To**: ContentDocument

### DateGenerated

- **Type**: date

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The date on which the PDF is generated.

### DocumentGenerationProcessId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The ID of the document generation process that contains the information used to create the PDF invoice.

This field is a relationship field.

- **Relationship Name**: DocumentGenerationProcess

- **Refers To**: DocumentGenerationProcess

### DocumentNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. A unique number assigned to the PDF invoice document.

### ErrorMessage

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: Any errors that occur during PDF generation.

### InvoiceId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the Invoice to which the Invoice Doc is attached.

This field is a relationship field.

- **Relationship Name**: Invoice

- **Relationship Type**: Master-detail

- **Refers To**: Invoice (the master object)

### Status

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The status of the PDF generation process.

Valid values are `Blocked`, `Cancelled`, `Failure`, `Pending`, or `Success`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[InvoiceDocumentFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[InvoiceDocumentHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoicedocument.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
