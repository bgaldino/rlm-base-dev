---
page_id: sforce_api_objects_assetdowntimeperiod.htm
title: AssetDowntimePeriod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetdowntimeperiod.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetDowntimePeriod

Represents a period during which an asset is not able to perform as expected.
Downtime periods include planned activities, such as maintenance, and unplanned events, such
as mechanical breakdown. This object is available in API version 49.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`, `getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssetDowntimePeriodNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The unique number of this asset downtime period record. |
| AssetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the asset this asset downtime period record is for. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  The description of this asset downtime period. |
| DowntimeType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of this asset downtime period. Possible values are:  - `Planned` - `Unplanned` |
| EndTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The time this asset downtime period ended. |
| IsExcluded | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Whether this asset downtime period is excluded from the calculation of accumulated downtime and accumulated unplanned downtime, and therefore not included in availability and reliability calculations. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed. |
| StartTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The time this asset downtime period started. |
