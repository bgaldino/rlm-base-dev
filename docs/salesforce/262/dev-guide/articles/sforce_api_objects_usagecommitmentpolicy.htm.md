---
page_id: sforce_api_objects_usagecommitmentpolicy.htm
title: UsageCommitmentPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usagecommitmentpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# UsageCommitmentPolicy

Represents the set of rules that determines how commitments are
applied to a usage resource. This object is available in API version 65 and
later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

## Fields

| Field | Details |
| --- | --- |
| CommitmentRate | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The rate that’s applicable to the usage resource’s units consumed post the commitment is utilized, but the commitment period is still active.  Valid values are:  - `Bounded Object   Rate` - `Lowest Commitment   Rate`  The default value is `Lowest Commitment Rate`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Date and time when the current user last viewed or modified this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Date and time when the current user last viewed or modified this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the usage commitment policy. |
