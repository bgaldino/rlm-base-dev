---
page_id: sforce_api_objects_usageoveragepolicy.htm
title: UsageOveragePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usageoveragepolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# UsageOveragePolicy

Represents the set of rules that determine the management of usage resource’s
units consumed beyond the granted limit. This object is available in API version 65
and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Date and time when the current user last viewed or modified this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Date and time when the current user last viewed or modified this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the usage overage policy. |
| OverageChargeable | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies whether the overconsumption beyond the granted quantity is to be charged.  Valid values are:  - `No` - `Yes` |
