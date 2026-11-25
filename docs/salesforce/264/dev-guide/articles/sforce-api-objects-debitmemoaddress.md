---
page_id: sforce-api-objects-debitmemoaddress
title: DebitMemoAddress
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-debitmemoaddress.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_debitmemoaddress.htm
fetched_at: 2026-11-25
---

# DebitMemoAddress

Represents the buyer’s address information, which is used to determine the tax amount for a buyer when a debit memo is issued. This object is available in API version 65.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and one of these permission sets to access this object.

- Billing Admin permission set

- Billing Operations User permission set

- Payments Admin permission set

- Payments Operation User permission set

- Credit Memo Operations User permission set

## Fields

### Address

- **Type**: address

- **Properties**: Filter

- **Description**: The billing or shipping address of the debit memo.

### DebitMemoAddressNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The auto-generated reference number for the debit memo address.

### DebitMemoId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the debit memo associated with the address.

This field is a relationship field.

- **Relationship Name**: DebitMemo

- **Relationship Type**: Master-detail

- **Refers To**: DebitMemo (the master object)

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed a debit memo address record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a debit memo address record. If this value is null, it’s possible that the user only accessed the debit memo address record or a related list view (`LastReferencedDate`), but not viewed the debit memo address record itself.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[DebitMemoAddressHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-debitmemoaddress.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
