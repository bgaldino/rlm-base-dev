---
page_id: sforce_api_objects_pricing_contractitemprice.htm
title: ContractItemPrice
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricing_contractitemprice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ContractItemPrice

Represents the price of a product on the contract. This object is
available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ContractId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The contract record associated with this contract item price record.  This field is a relationship field.  Relationship Name  Contract  Relationship Type  Master-detail  Refers To  Contract (the master object) |
| CurrencyIsoCode | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Contains the ISO code for any currency allowed by the organization. Available only if the multicurrency feature is enabled.  Valid value is:  - `USD`—U.S.   Dollar  The default value is `USD`. |
| DiscountType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit of the discount.  Valid values are:  - `AdjustmentAmount` - `AdjustmentPercentage` |
| DiscountValue | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The value of the discount. |
| EndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time till when the contract item price is no longer in effect. |
| ItemId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the line item record associated with this contract item price record.  This field is a polymorphic relationship field.  Relationship Name  Item  Relationship Type  Lookup  Refers To  Product2, ProductCategory |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the contract item price record. |
| Price | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The unit price of the product that’s being sold as part of the contract. |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the product selling model record associated with this contract item price record.  This field is a relationship field.  Relationship Name  ProductSellingModel  Relationship Type  Lookup  Refers To  ProductSellingModel |
| SellingModelType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether the line item is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term.  Valid values are:  - `Evergreen` - `OneTime` - `TermDefined`  The default value is `OneTime`. |
| StartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the contract item price comes into effect. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ContractItemPriceFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ContractItemPriceHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
