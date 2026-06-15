---
page_id: sforce_api_objects_invoicelinerelationship.htm
title: InvoiceLineRelationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoicelinerelationship.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# InvoiceLineRelationship

Represents a relationship between invoice line items to support
bundles where one parent invoice line has multiple child invoice lines. This object is
available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AssociatedInvoiceLineId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the related invoice line record. In a bundle relationship, this invoice line is the child.  This field is a relationship field.  Relationship Name  AssociatedInvoiceLine  Refers To  InvoiceLine |
| AssociatedInvoiceLinePricing | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes how the related invoice line is priced relative to the primary invoice line.  Valid values are:  - `IncludedInBundlePrice` - `NotIncludedInBundlePrice` |
| AssociatedInvoiceLineRole | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes the role of the related invoice line in the relationship. The value is derived from the AssociatedProductRoleCat field of the ProductRelationshipType object.  Valid values are:  - `AddOnComponent` - `BundleComponent` - `ClassificationComponent` - `SetComponent` |
| InvoiceId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the related invoice record.  This field is a relationship field.  Relationship Name  Invoice  Refers To  Invoice |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed an invoice line relationship record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed an invoice line relationship record. If this value is null, it’s possible that the user only accessed the invoice line relationship record or a related list view (`LastReferencedDate`), but not viewed the invoice line relationship record itself. |
| MainInvoiceLineId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the primary invoice line record. In a bundle relationship, this invoice line is the parent.  This field is a relationship field.  Relationship Name  MainInvoiceLine  Relationship Type  Master-detail  Refers To  InvoiceLine (the master object) |
| MainInvoiceLineRole | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes the role of the primary invoice line in the relationship. The value is derived from the MainProductRoleCat field of the ProductRelationshipType object.  Valid values are:  - `AddOn` - `Bundle` - `Set` |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number identifying the invoice line relationship. |
| ProductRelationshipTypeId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the product relationship type record between the main and associated invoice lines.  This field is a relationship field.  Relationship Name  ProductRelationshipType  Refers To  ProductRelationshipType |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[InvoiceLineRelationshipFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[InvoiceLineRelationshipHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
