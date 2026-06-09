---
page_id: sforce_api_objects_quoteaction.htm
title: QuoteAction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quoteaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# QuoteAction

Indicates the type of sales transaction that’s being quoted; for
example, a renewal sale. This object is available in API version 59.0 and
later.

If a quote doesn't have a quote action, Salesforce treats it as a quote of the `Add` type. When such a quote is used to create an order,
Salesforce automatically creates an order action of the `Add` type.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

This object is available in orgs with Revenue Cloud. It’s also available in Industries
Automotive and Industries Field Service.

## Fields

| Field | Details |
| --- | --- |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  ISO code of the currency. Use only one of the valid alphabetic, three-letter currency ISO codes defined by the ISO 4217 standard, such as `USD`, `GBP`, or `JPY`. Must be unique within your organization. Label is **Currency ISO Code**.  The default value is `USD`.  See [Supported Currencies (ICU)](https://help.salesforce.com/s/articleView?id=xcloud.admin_supported_currencies.htm&type=5&language=en_US "HTML (New Window)") for a list of currency codes Salesforce supports. This field is available in Revenue Cloud in API version 66.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, the user accessed this record or list view indirectly, but didn’t view it. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name given to the quote action. |
| QuoteId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The quote related to this quote action.  This field is a relationship field.  Relationship Name  Quote  Relationship Type  Lookup  Refers To  Quote |
| SourceAssetId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The asset changed by this sales transaction. For example, if the quote action is a quantity amendment, this field contains the ID of the asset that’s amended.  This field is a relationship field.  Relationship Name  SourceAsset  Relationship Type  Lookup  Refers To  Asset |
| Subtype | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The subtype of the action on the quote line item.  Valid values are:  - `DowngradeFrom`—Available in API version 66.0   and later. - `DowngradeTo`—Available in API version 66.0   and later. - `FieldAmendment` - `Rollback` - `StartDateAdjustment` - `SwapIn`—Available   in API version 66.0 and later. - `SwapOut`—Available in API version 66.0 and   later. - `TransferFrom` - `TransferTo` - `UpgradeFrom`—Available in API version 66.0   and later. - `UpgradeTo`—Available in API version 66.0 and   later.  This field is available with Revenue Cloud in API version 64.0 and later. |
| Type | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The type of sales transaction that the related quote is for.  Valid values are:  - `Add` - `Amend` - `Association`—Available in API version 66.0   and later. - `Cancel` - `No Change` - `Renew` - `Transfer`—Available with Revenue Cloud in API   version 65.0 and later. |
