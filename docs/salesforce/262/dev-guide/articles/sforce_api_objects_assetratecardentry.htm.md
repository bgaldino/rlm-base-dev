---
page_id: sforce_api_objects_assetratecardentry.htm
title: AssetRateCardEntry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetratecardentry.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetRateCardEntry

Stores the negotiated rate card entries that are associated with an
asset in Revenue Cloud. This object is available in API version 62.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`

## Special Access Rules

This object is available in orgs where Revenue Cloud is enabled.

## Fields

| Field | Details |
| --- | --- |
| AssetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the asset rate card entry record.  This field is a relationship field.  Relationship Name  Asset  Relationship Type  Master-detail  Refers To  Asset (the master object) |
| BindingObjectFormula | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The formula that returns the ID of the associated binding object, if specified. If binding object isn't added, the formula returns the asset ID of the asset related to this asset rate card entry. This field is read-only. Available in API version 65.0 and later. |
| BindingObjectId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the binding object associated with the asset rate card entry. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  BindingObject  Refers To  Asset |
| BindingObjectRateOrder | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The order that determines the applicable binding object rate when multiple rates are defined for an Anchor binding object within a effective period. Available in API version 65.0 and later. |
| CurrencyIsoCode | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The ID of the binding object associated with the asset rate card entry.  Possible values are:  - AED - UAE Dirham - AUD - Australian Dollar - BRL - Brazilian Real - CAD - Canadian Dollar - EUR - Euro - GBP - British Pound - INR - Indian Rupee - JPY - Japanese Yen - SEK - Swedish Krona - USD - U.S. Dollar  The default value is USD. Available in API version 65.0 and later. |
| EndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date when the rate card's time period becomes inactive. The rate card becomes inactive at 11:59:00 PM on the end date. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  An auto-generated number assigned to the asset rate card entry. Read-only. |
| NegotiatedRate | Type  double  Properties  Create, Filter, Sort, Update  Description  The base negotiated rate used to charge overage consumption. |
| RateCardEntryId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the rate card entry record containing the catalog rates that's associated with the asset rate card entry.  This field is a relationship field.  Relationship Name  RateCardEntry  Refers To  RateCardEntry |
| RateCardId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the rate card record that's associated with the asset rate card entry.  This field is a relationship field.  Relationship Name  RateCard  Refers To  RateCard |
| RateUnitOfMeasureId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the unit of measure record that's associated with the asset rate card entry.  This field is a relationship field.  Relationship Name  RateUnitOfMeasure  Refers To  UnitOfMeasure |
| StartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date when the rate card's time period becomes active. The rate card becomes active at 12:00:00 AM on the start date. |
| UsageResourceId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the usage resource record that's associated with the asset rate card entry.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |
