---
page_id: sforce-api-objects-taxtreatmentitem
title: Tax Treatment Item
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-taxtreatmentitem.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_taxtreatmentitem.htm
fetched_at: 2026-11-25
---

# Tax Treatment Item

Represents tax code information that’s used to calculate tax for a product by a specific tax engine. This object is available in API version 66.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Billing Admin permission set or Tax Admin permission set to access this object.

## Fields

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Additional details about the tax treatment item.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed a tax treatment item record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a tax treatment item record. If this value is null, it’s possible that the user only accessed the tax treatment item record or a related list view (`LastReferencedDate`), but not viewed the tax treatment item record itself.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The name of the tax treatment item.

### ProductCode

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The code of the product that the tax treatment item applies to.

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The ID of the product that the tax treatment item applies to.

This field is a relationship field.

- **Relationship Name**: Product

- **Refers To**: Product2

### TaxCode

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The reference code that’s used when an external tax engine calculates tax.

### TaxTreatmentId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Required. The parent tax treatment associated with the tax treatment item record.

This field is a relationship field.

- **Relationship Name**: TaxTreatment

- **Relationship Type**: Master-detail

- **Refers To**: TaxTreatment (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-taxtreatmentitem.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
