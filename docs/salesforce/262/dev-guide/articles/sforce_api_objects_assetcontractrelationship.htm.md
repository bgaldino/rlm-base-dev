---
page_id: sforce_api_objects_assetcontractrelationship.htm
title: AssetContractRelationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetcontractrelationship.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetContractRelationship

Represents a relationship between an asset and a contract. This
object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

This object is available in Enterprise, Unlimited, and Developer Editions of Revenue
Cloud.

## Fields

| Field | Details |
| --- | --- |
| AssetId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the asset related to the contract.  This field is a relationship field.  Relationship Name  Asset  Relationship Type  Lookup  Refers To  Asset |
| ContractId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the contract related to the asset.  This field is a relationship field.  Relationship Name  Contract  Relationship Type  Lookup  Refers To  Contract |
| EndDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The end date and time of the relationship between contract and asset. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. The associated UI label is **Last Modified Date**. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, the user accessed this record or list view (LastReferencedDate) but didn’t view it. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The auto-generated number assigned to AssetContractRelationship. (Read Only) |
| StartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The start date and time of the relationship between contract and asset. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssetContractRelationshipFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssetContractRelationshipHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.
