---
page_id: sforce_api_objects_invoicedocument.htm
title: InvoiceDocument
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoicedocument.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# InvoiceDocument

Represents the PDF document generated for an invoice. This object is
available in API version 63.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need Revenue Cloud Billing license, and the Billing Admin permission set or the
Billing Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| ContentDocumentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the generated PDF document.  This field is a relationship field.  Relationship Name  ContentDocument  Refers To  ContentDocument |
| DateGenerated | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date on which the PDF is generated. |
| DocumentGenerationProcessId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the document generation process that contains the information used to create the PDF invoice.  This field is a relationship field.  Relationship Name  DocumentGenerationProcess  Refers To  DocumentGenerationProcess |
| DocumentNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. A unique number assigned to the PDF invoice document. |
| ErrorMessage | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Any errors that occur during PDF generation. |
| InvoiceId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the Invoice to which the Invoice Doc is attached.  This field is a relationship field.  Relationship Name  Invoice  Relationship Type  Master-detail  Refers To  Invoice (the master object) |
| Status | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The status of the PDF generation process.  Valid values are:  - `Blocked` - `Cancelled` - `Failure` - `Pending` - `Success` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[InvoiceDocumentFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[InvoiceDocumentHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
