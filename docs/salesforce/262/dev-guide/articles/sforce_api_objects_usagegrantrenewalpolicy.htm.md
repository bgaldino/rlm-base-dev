---
page_id: sforce_api_objects_usagegrantrenewalpolicy.htm
title: UsageGrantRenewalPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usagegrantrenewalpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# UsageGrantRenewalPolicy

Represents a policy about the rollover of a usage grant. This
object is available in API version 62.0 and later.

A usage grant renewal policy is used if you want to never renew a usage grant or renew
on a specific frequency.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  A unique user-defined string for the usage grant renewal policy. |
| IsRenewalAllowed | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the policy renewal is allowed (`true`) or not (`false`). If `true`, then the policy can be renewed.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the renewal policy record. |
| RenewalFrequency | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The frequency of the policy renewals, when used with the RenewalFrequencyUnit field. |
| RenewalFrequencyUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The renewal duration for a policy.  Valid values are:  - `Month` - `Quarter` - `Year` |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the renewal policy.  Valid values are:  - `Active` - `Draft` - `Inactive` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[UsageGrantRenewalPolicyFeed](https://developer.salesforce.com/docs/./sforce_api_associated_objects_feed.htm.md)
:   Feed tracking is available for the object.

[UsageGrantRenewalPolicyHistory](https://developer.salesforce.com/docs/./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.
