---
page_id: sforce_api_objects_usageresourcebillingpolicy.htm
title: UsageResourceBillingPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usageresourcebillingpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# UsageResourceBillingPolicy

Represents information about how the usage is accumulated before
rating a usage resource.This object is available in API version 62.0 and
later.

A usage resource billing policy object is used to configure the properties of usage
resources related to how aggregation is performed on the usage records before rating.
Usage resource billing policies are defined at the usage resource level and can be
reused across multiple usage resources.

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

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  A unique user-defined string for the usage resource billing policy. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the usage resource billing policy record. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the policy.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| UsageAccumulationMethod | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update, Defaulted On Create  Description  The method used to accumulate the usage.  Valid values are:  - `Peak` - `Sum` |
| UsageAccumulationPeriod | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The duration for which the usage is accumulated.  Valid values are:  - `Daily` - `Monthly` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[UsageResourceBillingPolicyFeed](./sforce_api_associated_objects_feed.htm.md)
:   Feed tracking is available for the object.

[UsageResourceBillingPolicyHistory](./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.
