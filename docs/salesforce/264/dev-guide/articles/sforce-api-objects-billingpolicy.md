---
page_id: sforce-api-objects-billingpolicy
title: BillingPolicy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingpolicy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_billingpolicy.htm
fetched_at: 2026-11-25
---

# BillingPolicy

Represents information about a set of billing treatments that define the rules to invoice a customer for an order item. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### BillingTreatmentSelection

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Required. Defines how billing treatments are assigned to order items and assets that are related to the billing policy.

Valid values are `Default`, `LegalEntity`, or `Manual`.

### DefaultBillingTreatmentId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: When `BillingTreatmentSelection` has a value of `Default`, the selected billing treatment is used for all the order items and assets that are related to the billing policy.

This field is a relationship field.

- **Relationship Name**: DefaultBillingTreatment

- **Refers To**: BillingTreatment

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Additional details about the billing policy.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed a billing policy indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a billing policy. If this value is null, it’s possible that the user only accessed the billing policy or a related list view (`LastReferencedDate`), but not viewed the accounting period itself.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The name of the billing policy.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Required. The status of the billing policy.

Valid values are `Active`, `Draft`, or `Inactive`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[BillingPolicyHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingpolicy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
