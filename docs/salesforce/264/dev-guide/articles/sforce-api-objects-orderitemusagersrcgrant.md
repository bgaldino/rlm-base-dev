---
page_id: sforce-api-objects-orderitemusagersrcgrant
title: OrderItemUsageRsrcGrant
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemusagersrcgrant.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_orderitemusagersrcgrant.htm
fetched_at: 2026-11-25
---

# OrderItemUsageRsrcGrant

Represents the negotiated grants for the usage resource that’s associated with the usage product added in the order item. This object is available in API version 65.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

### GrantQuantity

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The granted or negotiated quantity of a usage resource associated with the usage product.

### GrantType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Specifies the type of model that defines how the usage resource is consumed.

Valid values are `Commit` or `Grant`.

The default value is `Grant`.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The auto-generated identifier for the order item usage resource grant record. For example, OIURG-00004 or OIURG-4567.

### OrderItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The order item associated with the usage product.

This field is a relationship field.

- **Relationship Name**: OrderItem

- **Relationship Type**: Master-detail

- **Refers To**: OrderItem (the master object)

### ProductUsageGrantId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The product usage grant associated with the order item.

This field is a relationship field.

- **Relationship Name**: ProductUsageGrant

- **Refers To**: ProductUsageGrant

### TokenResourceId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage resource of category Token associated with the usage resource related to the usage product added in the order item.

This field is a relationship field.

- **Relationship Name**: TokenResource

- **Refers To**: UsageResource

### UsageGrantRefreshPolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage grant refresh policy associated with the usage resource related to the usage product added in the order item.

This field is a relationship field.

- **Relationship Name**: UsageGrantRefreshPolicy

- **Refers To**: UsageGrantRenewalPolicy

### UsageGrantRolloverPolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage grant rollover policy associated with the usage resource related to the usage product added in the order item.

This field is a relationship field.

- **Relationship Name**: UsageGrantRolloverPolicy

- **Refers To**: UsageGrantRolloverPolicy

### UsageResourceId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The usage resource associated with the usage product that’s added in the order item.

This field is a relationship field.

- **Relationship Name**: UsageResource

- **Refers To**: UsageResource

### ValidityPeriodTerm

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The duration for which the usage resource grant is valid, when used with the validity period units.

### ValidityPeriodUnit

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The length of a validity period for the usage resource grant, when used with the validity period term.

Valid values are `Month`, `None`, or `Year`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemusagersrcgrant.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
