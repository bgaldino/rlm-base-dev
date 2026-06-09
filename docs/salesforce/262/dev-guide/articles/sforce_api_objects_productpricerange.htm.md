---
page_id: sforce_api_objects_productpricerange.htm
title: ProductPriceRange
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productpricerange.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductPriceRange

Represents the price range of a product determined by using a product
selling model that’s stored in the relevant price book. This object is available in
API version 62.0 and later.

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
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  ISO code for any currency allowed by the organization. Available only for organizations with the multicurrency feature enabled.  Valid values are:  - `BHD`—Bahraini   Dinar - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is `USD`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates whether the product price range has been archived (`true`) or not (`false`). This field is read-only. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the product price range. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The Salesforce ID of the sales representative who owns the product price range.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The product for which the price range is being determined.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The product selling model used to determine the price range of the product.  This field is a relationship field.  Relationship Name  ProductSellingModel  Refers To  ProductSellingModel |
| RecordedPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  The selected price of the product over a range of prices. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductPriceRangeFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductPriceRangeHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[ProductPriceRangeShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
