---
page_id: sforce_api_objects_invoiceaddressgroup.htm
title: InvoiceAddressGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceaddressgroup.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# InvoiceAddressGroup

Represents the storage of the buyer's address information. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`

## Special Access Rules

You need the Billing Operations User permission set to access this object.

## Fields

### Address

- **Type**: address
- **Properties**: Filter, Nillable
- **Description**: The buyer's address. See [Compound Field Considerations and Limitations](https://developer.salesforce.com/docs/atlas.en-us.264.0.api.meta/api/compound_fields_limitations.htm#compound_fields_limitations "HTML (New Window)") for details on geolocation compound fields.

### InvoiceAddressGroupNumber

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: Required. The auto-generated reference number for the invoice address group.

### InvoiceId

- **Type**: reference
- **Properties**: Filter, Group, Sort
- **Description**: Required. The ID of the invoice associated with the address group.

This field is a relationship field.

- **Relationship Name**: Invoice
- **Relationship Type**: Master-detail
- **Refers To**: Invoice (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceaddressgroup.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
