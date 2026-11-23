---
page_id: sforce_api_objects_sequencegapreconciliation.htm
title: SequenceGapReconciliation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_sequencegapreconciliation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# SequenceGapReconciliation

Represents a missing sequence value identified during reconciliation, which can be used later to ensure there are no gaps in the sequence policy numbers. This object is available in API version 65.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### LastReferencedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last accessed sequence gap reconciliation record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last viewed a sequence gap reconciliation record. If this value is null, it’s possible that the user only accessed the sequence gap reconciliation record or a related list view (LastReferencedDate), but not viewed the sequence gap reconciliation record itself.

### OwnerId

- **Type**: reference
- **Properties**: Filter, Group, Sort
- **Description**: Required. The ID of the user who owns a sequence gap reconciliation record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Refers To**: Group, User

### SequenceGapReconciliationNumber

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: Required. The reconciled sequence pattern value.

### SequencePolicyId

- **Type**: reference
- **Properties**: Filter, Group, Sort
- **Description**: Required. The parent sequence policy associated with the gap reconciliation. Deleting a sequencing policy automatically removes all its associated criteria.

This field is a relationship field.

- **Relationship Name**: SequencePolicy
- **Refers To**: SequencePolicy

### SequenceValue

- **Type**: long
- **Properties**: Filter, Group, Sort
- **Description**: Required. The number that was missed during sequence policy generation.

### Status

- **Type**: picklist
- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort
- **Description**: The current status of the missed number.

Valid values are `Assigned`, `Blocked`, `Unassigned`, or `Under Review`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_sequencegapreconciliation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
