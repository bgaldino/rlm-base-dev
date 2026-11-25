---
page_id: sforce-api-objects-creditmemoaddressgroup
title: CreditMemoAddressGroup
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-creditmemoaddressgroup.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_creditmemoaddressgroup.htm
fetched_at: 2026-11-25
---

# CreditMemoAddressGroup

Represents the storage of the buyer’s address information, which is used to determine the tax credit amount for a buyer when a credit memo is issued. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`

## Special Access Rules

You need the Credit Memo Operations User permission set to access this object.

## Fields

### Address

- **Type**: address

- **Properties**: Filter, Nillable

- **Description**: The buyer’s address.

### CreditMemoAddressGroupNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The auto-generated reference number for the credit memo address group.

### CreditMemoId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the credit memo associated with the address group.

This field is a relationship field.

- **Relationship Name**: CreditMemo

- **Relationship Type**: Master-detail

- **Refers To**: CreditMemo (the master object)

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed a credit memo address group record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a credit memo address group record. If this value is null, it’s possible that the user only accessed the credit memo address group record or a related list view (`LastReferencedDate`), but not viewed the credit memo address group record itself.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-creditmemoaddressgroup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
