---
page_id: sforce-api-objects-pymtschddistributionmethod
title: PymtSchdDistributionMethod
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pymtschddistributionmethod.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_pymtschddistributionmethod.htm
fetched_at: 2026-11-25
---

# PymtSchdDistributionMethod

Represents information about the partial payments that the total payment is divided into. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the Payment Operations User permission set to access this object.

## Fields

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The user-entered details of the payment schedule distribution method.

### DistributionCount

- **Type**: int

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The number of payment schedule items for the payment schedule. The payment schedule items are used to distribute the payment schedule’s total payment into partial payments.

### DistributionMethodType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Required. The time interval of the payment distribution method.

Valid value is:

- `FullDistribution`—The full amount on the payment schedule is distributed to a single payment schedule item.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferenceDate` is not null, the user accessed this record or list view indirectly.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The user-entered name for the payment schedule distribution method.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Required. The ID of the owner of the PaymentScheduleDistributionMethod record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PymtSchdDistributionMethodHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pymtschddistributionmethod.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
