---
page_id: sforce_api_objects_prorationpolicy.htm
title: ProrationPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_prorationpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProrationPolicy

Represents the proration policy associated with a Product Selling Model
Option that determines how a product's price is calculated based on subscription duration
or billing periods. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `describeLayout()`, `describeSObjects()`,
`getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Fields

| Field | Details |
| --- | --- |
| ArePartialPeriodsAllowed | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates whether partial periods should be allowed for standard time periods.  The default value is false. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the proration policy was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the proration policy was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort  Description  The name of the proration policy. |
| ProrationPolicyType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The type of proration policy to be used.  Possible values are:  - `StandardTimePeriods`—Standard Time   Periods |
| RemainderStrategy | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The type of remainder strategy to be used. |
