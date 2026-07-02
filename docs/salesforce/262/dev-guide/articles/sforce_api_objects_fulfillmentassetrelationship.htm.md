---
page_id: sforce_api_objects_fulfillmentassetrelationship.htm
title: FulfillmentAssetRelationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentassetrelationship.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# FulfillmentAssetRelationship

Represents a relationship between two fulfillment assets. This
object is available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssociatedFulfillAssetRole | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The role of the associated fulfillment asset.  Valid values are:  - `BundleComponent` - `ClassificationComponent`—Product   Classification Component |
| AssociatedFulfillmentAssetId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The name of the associated fulfillment asset.  This field is a relationship field.  Relationship Name  AssociatedFulfillmentAsset  Refers To  FulfillmentAsset |
| EndTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The time until when this asset relationship is valid. |
| MainFulfillmentAssetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The name of the primary fulfillment asset.  This field is a relationship field.  Relationship Name  MainFulfillmentAsset  Relationship Type  Master-detail  Refers To  FulfillmentAsset (the master object) |
| MainFulfillmentAssetRole | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The role of the primary fulfillment asset.  Valid value is `Bundle Parent`. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the fulfillment asset relationship. |
| ProductRelationshipTypeId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The type of relationship between two assets.  This field is a relationship field.  Relationship Name  ProductRelationshipType  Refers To  ProductRelationshipType |
| StartTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The time from when this asset relationship is valid. |
