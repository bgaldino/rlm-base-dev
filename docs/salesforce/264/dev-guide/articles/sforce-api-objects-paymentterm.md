---
page_id: sforce-api-objects-paymentterm
title: PaymentTerm
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-paymentterm.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_paymentterm.htm
fetched_at: 2026-11-25
---

# PaymentTerm

Represents an agreement between a buyer and a seller about when payment is due for an invoice. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Additional details about the payment term.

### IsDefault

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Required. Indicates whether the payment term is the default term for your Salesforce org (`true`) or not (`false`).

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferenceDate` field is not null, the user accessed this record or list view indirectly.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The name of the payment term. This name appears on the invoice.

### Status

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Required. Specifies whether the payment term is available for use on invoices.

Possible values are `Active`, `Draft`, or `Inactive`

The default value is `Draft`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PaymentTermHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-paymentterm.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
