---
page_id: sforce_api_objects_costbookentry.htm
title: CostBookEntry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_costbookentry.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CostBookEntry

Represents the total cost of a product or service that’s determined
based on various factors that affect a product's price. For example, when a product is
manufactured, the weight of the raw material can be a cost factor based on the amount of
material required and its shipping cost. This object is available in API version 61.0
and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| Cost | Type  currency  Properties  Create, Filter, Sort, Update  Description  Total cost of the product. |
| CostBookId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the Cost Book record with which this record is associated.  This field is a relationship field.  Relationship Name  CostBook  Relationship Type  Master-detail  Refers To  CostBook (the master object) |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  ISO code for any currency allowed by the organization. Available only for organizations with the multicurrency feature enabled.  Valid values are:  - `BHD`—Bahraini   Dinar - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is `USD`. |
| Description | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Description of this cost book entry record. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  Date and time when the cost book entry comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Date and time till when the cost book entry is no longer in effect. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Name of the cost book entry. |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. ID of the Product2 record with which this record is associated. This field must be specified when creating Product2 records. This field can’t be changed in an update.  This field is a relationship field.  Relationship Name  Product  Relationship Type  Lookup  Refers To  Product2 |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[CostBookEntryFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CostBookEntryHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
