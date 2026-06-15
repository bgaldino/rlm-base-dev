---
page_id: sforce_api_objects_bsgrelationship.htm
title: BsgRelationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_bsgrelationship.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BsgRelationship

Represents a relationship between billing schedule groups to support
bundles where one parent billing schedule group has multiple child billing schedule
groups. This object is available in API version 62.0 and later.

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
| AssociatedBsgId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the related billing schedule group. In a bundle relationship, this billing schedule group is the child.  This field is a relationship field.  Relationship Name  AssociatedBsg  Refers To  BillingScheduleGroup |
| AssociatedBsgPricing | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes how the related billing schedule group is priced relative to the primary billing schedule group.  Valid values are:  - `IncludedInBundlePrice` - `NotIncludedInBundlePrice` |
| AssociatedBsgRole | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes the role of the related billing schedule group in the relationship.  Valid values are:  - `AddOnComponent` - `BundleComponent` - `ClassificationComponent` - `SetComponent` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a billing schedule group record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a billing schedule group relationship record. If this value is null, it’s possible that the user only accessed the billing schedule group relationship record or a related list view (LastReferencedDate), but not viewed the billing schedule group relationship record itself. |
| MainBsgId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the primary billing schedule group. In a bundle relationship, this billing schedule group is the parent.  This field is a relationship field.  Relationship Name  MainBsg  Relationship Type  Master-detail  Refers To  BillingScheduleGroup (the master object) |
| MainBsgRole | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. This field describes the role of the primary billing schedule group in the relationship.  Valid values are:  - `AddOn` - `Bundle` - `Set` |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the billing schedule relationship. |
| ProductRelationshipTypeId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the relationship type between the main and associated billing schedule group.  This field is a relationship field.  Relationship Name  ProductRelationshipType  Refers To  ProductRelationshipType |
