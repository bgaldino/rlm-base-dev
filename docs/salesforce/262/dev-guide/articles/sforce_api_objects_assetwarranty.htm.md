---
page_id: sforce_api_objects_assetwarranty.htm
title: AssetWarranty
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetwarranty.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetWarranty

Defines the warranty terms applicable to an asset along with any exclusions and
extensions. This object is available in API version 50.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`,
`search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the asset this warranty term applies to. |
| AssetWarrantyNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The identifier of the asset warranty record. |
| EndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date on which this warranty term expires. |
| ExchangeType | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The type of exchange offered by this warranty term. |
| Exclusions | Type  textarea  Properties  Create, Nillable, Update  Description  Description of any exclusions. |
| ExpensesCovered | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percentage of expenses covered. |
| ExpensesCoveredEndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date on which cover for expenses ends. |
| IsTransferable | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Defines whether the warranty term can be transferred to a new owner. |
| LaborCovered | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percentage of labor covered. |
| LaborCoveredEndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date on which cover for labor ends. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the asset warranty term was last modified. Its label in the user interface is Last Modified Date. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the asset warranty term was last viewed. |
| PartsCovered | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percentage of parts covered. |
| PartsCoveredEndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date on which cover for parts ends. |
| Pricebook2Id | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the price book item associated with this asset warranty term. |
| StartDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date on which cover under this warranty term starts. |
| WarrantyTermId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the warranty term this asset warranty term extends. |
| WarrantyType | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The type of the warranty. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available in
the specified API version and later.

[AssetWarrantyChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm "HTML (New Window)")
:   Change events are available for the object.
