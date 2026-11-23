---
page_id: sforce_api_objects_paymentschedulepolicy.htm
title: PaymentSchedulePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentschedulepolicy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# PaymentSchedulePolicy

Represents information about the configuration for the payment schedule. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the Payment Operations User permission set to access this object.

## Fields

### DefaultTreatmentId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The default payment schedule treatment.

This field is a relationship field.

- **Relationship Name**: DefaultTreatment
- **Refers To**: PaymentScheduleTreatment

### Description

- **Type**: textarea
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The user-entered description for the payment schedule policy.

### IsOrgDefault

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: If the payment schedule policy is the default policy for the org, this value is set to `true`. If not, this value is set to `false`. An org can have only one default payment policy.

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly.

### Name

- **Type**: string
- **Properties**: Create, Filter, Group, idLookup, Sort, Update
- **Description**: The user-entered name of the payment schedule policy.

### OwnerId

- **Type**: reference
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Required. The ID of the owner of the PaymentSchedulePolicy record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Refers To**: Group, User

### Status

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: The status of the payment schedule policy.

Valid values are `Active`, `Canceled`, `Draft`, or `Inactive`.

### TreatmentSelection

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Specifies the payment schedule treatment.

Valid value is:

- `Default`—Uses the payment schedule treatment indicated by the DefaultTreatmentId field.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PaymentSchedulePolicyHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentschedulepolicy.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
