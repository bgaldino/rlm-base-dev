---
page_id: sforce-api-objects-usagecommitmentpolicy
title: UsageCommitmentPolicy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usagecommitmentpolicy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-std-objects-parent
legacy_page_id: sforce_api_objects_usagecommitmentpolicy.htm
fetched_at: 2026-11-25
---

# UsageCommitmentPolicy

Represents the set of rules that determines how commitments are applied to a usage resource. This object is available in API version 65 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

## Fields

### CommitmentRate

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The rate that’s applicable to the usage resource’s units consumed post the commitment is utilized, but the commitment period is still active.

Valid values are `Bounded Object Rate` or `Lowest Commitment Rate`.

The default value is `Lowest Commitment Rate`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Date and time when the current user last viewed or modified this record, a record related to this record, or a list view.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Date and time when the current user last viewed or modified this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the usage commitment policy.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usagecommitmentpolicy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
