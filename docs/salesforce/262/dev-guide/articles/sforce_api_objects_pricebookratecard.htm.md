---
page_id: sforce_api_objects_pricebookratecard.htm
title: PriceBookRateCard
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricebookratecard.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PriceBookRateCard

Represents a junction between price book and rate card objects.
This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Auto-generated identifier for the price book rate card record. |
| PriceBookId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Price book ID that's associated with the rate cards IDs. For Quote, Order, and Contracts, the price book IDs identify the associated rate cards.  This field is a relationship field.  Relationship Name  PriceBook  Relationship Type  Master-detail  Refers To  Pricebook2 (the master object) |
| RateCardId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Rate card ID that's associated with the price book.  This field is a relationship field.  Relationship Name  RateCard  Relationship Type  Master-detail  Refers To  RateCard (the detail object) |
| RateCardType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Type of rate card associated with the price book.  Valid values are:  - `Attribute` - `Base` - `Tier` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[PriceBookRateCardFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[PriceBookRateCardHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
