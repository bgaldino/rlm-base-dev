---
page_id: sforce-api-objects-bsgrelationship
title: BsgRelationship
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bsgrelationship.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_bsgrelationship.htm
fetched_at: 2026-11-25
---

# BsgRelationship

Represents a relationship between billing schedule groups to support bundles where one parent billing schedule group has multiple child billing schedule groups. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### AssociatedBsgId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the related billing schedule group. In a bundle relationship, this billing schedule group is the child.

This field is a relationship field.

- **Relationship Name**: AssociatedBsg

- **Refers To**: BillingScheduleGroup

### AssociatedBsgPricing

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. This field describes how the related billing schedule group is priced relative to the primary billing schedule group.

Valid values are `IncludedInBundlePrice` or `NotIncludedInBundlePrice`.

### AssociatedBsgRole

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. This field describes the role of the related billing schedule group in the relationship.

Valid values are `AddOnComponent`, `BundleComponent`, `ClassificationComponent`, or `SetComponent`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed a billing schedule group record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a billing schedule group relationship record. If this value is null, it’s possible that the user only accessed the billing schedule group relationship record or a related list view (`LastReferencedDate`), but not viewed the billing schedule group relationship record itself.

### MainBsgId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the primary billing schedule group. In a bundle relationship, this billing schedule group is the parent.

This field is a relationship field.

- **Relationship Name**: MainBsg

- **Relationship Type**: Master-detail

- **Refers To**: BillingScheduleGroup (the master object)

### MainBsgRole

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. This field describes the role of the primary billing schedule group in the relationship.

Valid values are `AddOn`, `Bundle`, or `Set`.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The auto-generated reference number for the billing schedule relationship.

### ProductRelationshipTypeId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The ID of the relationship type between the main and associated billing schedule group.

This field is a relationship field.

- **Relationship Name**: ProductRelationshipType

- **Refers To**: ProductRelationshipType

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bsgrelationship.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
