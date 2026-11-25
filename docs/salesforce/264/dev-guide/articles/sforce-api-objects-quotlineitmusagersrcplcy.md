---
page_id: sforce-api-objects-quotlineitmusagersrcplcy
title: QuotLineItmUsageRsrcPlcy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotlineitmusagersrcplcy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_quotlineitmusagersrcplcy.htm
fetched_at: 2026-11-25
---

# QuotLineItmUsageRsrcPlcy

Represents the policies that are used for the usage resource that’s associated with the usage product added in the quote line item. This object is available in API version 65.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`, `upsert()`

## Fields

### DrawdownOrder

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Specifies the order that’s used to debit consumption of entitlements related to the usage resource from the usage entitlement bucket.

Valid values are `ExpiringFirst`, `GrantedFirst`, or `GrantedLast`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when this record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The auto-generated identifier for the quote line item usage resource policy record. For example, QLIURP-00004 or QLIURP-4567.

### ProductUsageResourcePolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The product usage resource policy associated with the quote line item.

This field is a relationship field.

- **Relationship Name**: ProductUsageResourcePolicy

- **Refers To**: ProductUsageResourcePolicy

### QuoteLineItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The quote line item associated with the usage product.

This field is a relationship field.

- **Relationship Name**: QuoteLineItem

- **Relationship Type**: Master-detail

- **Refers To**: QuoteLineItem (the master object)

### RatingFrequencyPolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The rating frequency policy associated with the usage resource related to the usage product added in the quote line item.

This field is a relationship field.

- **Relationship Name**: RatingFrequencyPolicy

- **Refers To**: RatingFrequencyPolicy

### UsageAggregationPolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage aggregation policy associated with the usage resource related to the usage product added in the quote line item.

This field is a relationship field.

- **Relationship Name**: UsageAggregationPolicy

- **Refers To**: UsageResourceBillingPolicy

### UsageCommitmentPolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage commitment policy associated with the usage resource related to the usage product added in the quote line item.

This field is a relationship field.

- **Relationship Name**: UsageCommitmentPolicy

- **Refers To**: UsageCommitmentPolicy

### UsageOveragePolicyId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage overage policy associated with the quote line item.

This field is a relationship field.

- **Relationship Name**: UsageOveragePolicy

- **Refers To**: UsageOveragePolicy

### UsageResourceId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The usage resource associated with the usage product that’s added in the quote line item.

This field is a relationship field.

- **Relationship Name**: UsageResource

- **Refers To**: UsageResource

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotlineitmusagersrcplcy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
