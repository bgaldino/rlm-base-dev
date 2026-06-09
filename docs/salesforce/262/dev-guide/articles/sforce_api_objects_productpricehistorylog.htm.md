---
page_id: sforce_api_objects_productpricehistorylog.htm
title: ProductPriceHistoryLog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productpricehistorylog.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductPriceHistoryLog

Stores historical pricing data based on the product's price
range. This object is available in API version 62.0 and later.

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
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  ISO code for any currency allowed by the organization. Available only for organizations with the multicurrency feature enabled.  Valid values are:  - `BHD`—Bahraini   Dinar - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is `USD`. |
| Date | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date when the product price history log record is created. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates whether the product price history log has been archived (`true`) or not (`false`). This field is read-only. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the product price history log. |
| ProductPriceRangeId | Type  reference  Properties  Create, Filter, Group, Sort  Description    The product price range associated with this product price history log record.  This field is a relationship field.  Relationship Name  ProductPriceRange  Relationship Type  Master-detail  Refers To  ProductPriceRange (the master object) |
| TrackedPrice | Type  currency  Properties  Create, Filter, Sort, Update  Description  The price for a product recorded for a particular date. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductPriceHistoryLogFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductPriceHistoryLogHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
