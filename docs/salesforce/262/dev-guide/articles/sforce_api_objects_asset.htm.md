---
page_id: sforce_api_objects_asset.htm
title: Asset
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_asset.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# Asset

Represents an item of commercial value, such as a product sold by your company or a competitor, that a customer has purchased.

## Supported Calls

`create()`, `delete()`, `describeLayout()`,
`describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  (Required) ID of the Account associated with this asset. Must be a valid account ID. Required if ContactId isn’t specified.  This field is a relationship field.  Relationship Name  Account  Relationship Type  Lookup  Refers To  Account |
| Address | Type  address  Properties  Filter, Nillable  Description  Represents the physical address or geolocation of the asset. |
| AssetLevel | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The asset’s position in an asset hierarchy. If the asset has no parent or child assets, its level is 1. Assets that belong to a hierarchy have a level of 1 for the root asset, 2 for the child assets of the root asset, 3 for their children, and so forth. On assets created before the introduction of this field, the asset level defaults to –1. After the asset record is updated, the asset level is calculated and automatically updated. |
| AssetProvidedById | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The account that provided the asset, typically a manufacturer.  This field is a relationship field.  Relationship Name  AssetProvidedBy  Relationship Type  Lookup  Refers To  Account |
| AssetServicedById | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The account in charge of servicing the asset.  This field is a relationship field.  Relationship Name  AssetServicedBy  Relationship Type  Lookup  Refers To  Account |
| AssetTypeId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The asset type associated with the asset.  This field is a relationship field.  This field is available in API version 62.0 and later for users with the Health Cloud Appointment Management permission set.  Relationship Name  AssetType  Relationship Type  Lookup  Refers To  AssetType |
| Availability | Type  percent  Properties  Filter, Nillable, Sort  Description  The percentage of expected uptime where the asset was available for use. |
| AveragetimetoRepair | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  Represents the number of hours it typically takes to repair an asset after a failure. |
| AveragetimeBetweenFailure | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  Represents the number of hours that typically elapses before the asset is likely to fail again. |
| AverageUptimePerDay | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The average number of hours per day the asset is expected to be available for use. |
| City | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The city detail for the address. |
| ConsequenceOfFailure | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The business impact associated with the asset’s failure. Using this field, you can address the asset’s health and take action using [Flows](https://help.salesforce.com/s/articleView?id=platform.flow.htm&type=5&language=en_US). To enable this field, use Object Manager to update the field availability. Make sure that the field is visible for field-level security and for page layout. To learn more, see [What Determines Field Access](https://help.salesforce.com/s/articleView?id=platform.customize_fieldaccess.htm&type=5&language=en_US). The picklist values aren’t predefined in orgs created before Winter ’22 that aren’t Field Service enabled. This field is available in API version 53.0 and later.  Possible values are:  - `Insignificant` - `Minor` - `Moderate` - `Major` - `Critical` |
| ContactId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Required if AccountId isn’t specified. ID of the Contact associated with this asset. Must be a valid contact ID that has an account parent (but doesn’t need to match the asset’s AccountId).  This field is a relationship field.  Relationship Name  Contact  Relationship Type  Lookup  Refers To  Contact |
| Country | Type  String  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The country detail for the address. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Three-letter ISO 4217 currency code associated with the invoice. The default value is USD.  This field is available in API version 55.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| CurrentAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  Reserved for future use. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| CurrentLifecycleEndDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Represents the end of the period shown as current. System-populated field inherited from the end date of the current asset state period. If that field is empty, as with an evergreen subscription, the Current Lifecycle End Date field is also empty. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| CurrentMrr | Type  currency  Properties  Filter, Nillable, Sort  Description  The asset’s monthly recurring revenue during the current asset state period. System-populated field inherited from the monthly recurring revenue on the current asset state period. If no asset state period is current, the value is `0`. Label is Current Monthly Recurring Revenue. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| CurrentQuantity | Type  double  Properties  Filter, Nillable, Sort  Description  The asset’s quantity during the current asset state period. System-populated field inherited from the quantity on the current asset state period. If no asset state period is current, the value is `0`. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  Description of the asset. |
| DigitalAssetStatus | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Status of digital tracking of the asset. The default picklist includes the following values:  - `On` - `Off` - `Warning` - `Error` |
| ExternalIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the matching record in an external system. This field is available in API version 49.0 and later. |
| GeocodeAccuracy | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Accuracy level of the geocode for the address. |
| HasLifecycleManagement | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  True if this asset is a lifecycle-managed asset, otherwise false. You can’t switch an asset to a lifecycle-managed asset or the reverse. This field is system populated.  The default value is `false`. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| InstallDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Date when the asset was installed. |
| IsCompetitorProduct | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this Asset represents a product sold by a competitor (`true`) or not (`false`). The default value is `false`. Its UI label is Competitor Asset. |
| IsInternal | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates that the asset is produced or used internally (`true`) or not (`false`). The default value is `false`. Its UI label is Internal Asset. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time that the asset was last modified. Its UI label is Last Modified Date. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time that the asset was last viewed. |
| Latitude | Type  double  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Used with Longitude to specify the precise geolocation of the address. |
| LifecycleEndDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Represents the end of the asset’s lifecycle. System-populated field inherited from the end date of the final asset state period. If that field is empty, as with an evergreen subscription, the lifecycle has no end date. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| LifecycleStartDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Represents the beginning of the asset’s lifecycle. System-populated field inherited from the start date of the earliest asset state period. This field can’t be edited. When a new asset action affects the start date of an asset state period, the period is deleted and a new one is generated. This field is available in API version 50.0 and later. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| LocationId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The asset’s location. Typically, this location is the place where the asset is stored, such as a warehouse or van.  If you have access to the location entity, it doesn’t necessarily mean you can access the location id field. To access the location, you must have userHasLocation user access. |
| Longitude | Type  double  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Used with Latitude to specify the precise geolocation of the address. |
| ManufactureDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date when the asset was manufactured. This field is available from API version 49.0 and later. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  (Required) Name of the asset. Label is Asset Name. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The asset’s owner. By default, the asset owner is the user who created the asset record. Its UI label is Asset Owner.  This field is a relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  User |
| ParentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The asset’s parent asset. Its UI label is Parent Asset.  This field is a relationship field.  Relationship Name  Parent  Relationship Type  Lookup  Refers To  Asset |
| PostalCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The postal code for the address. |
| Price | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  Price paid for this asset. |
| PricingSource | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Pricing source to use when amending or renewing an asset.  Valid values are:  - `LastTransaction`—Last   Transaction - `PriceBookListPrice`—Price Book or   List Price   Available in API version 60.0 and later. |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  (Optional) ID of the Product2 associated with this asset. Must be a valid Product2 ID. Its UI label is Product.  This field is a relationship field.  Relationship Name  Product2  Relationship Type  Lookup  Refers To  Product2 |
| ProductCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The product code of the related product. |
| ProductDescription | Type  string  Properties  Filter, Sort, Nillable  Description  The product description of the related product. |
| ProductFamily | Type  picklist  Properties  Filter, Group, Sort, Nillable  Description  The product family of the related product. |
| PurchaseDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Date on which this asset was purchased. |
| Quantity | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  Quantity purchased or installed. The Quantity field value isn’t set by Customer Asset Lifecycle Management. Instead, you can populate the field as you need. |
| QuantityIncreasePricingType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specify which pricing type to use when the quantity of this asset is increased. Its UI label is Pricing Type for Quantity Increase. This field is available in API version 56.0 and later. This field is available when Revenue Cloud is enabled.  Possible values are:  - `LastNegotiatedPrice`—Available   in API version 58.0 and later. - `ListPrice` |
| RecordTypeId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The unique identifier for the asset.  This field is a relationship field.  Relationship Name  RecordType  Relationship Type  Lookup  Refers To  RecordType |
| Reliability | Type  percent  Properties  Filter, Nillable, Sort  Description  The percentage of expected uptime where the asset wasn’t subject to unplanned downtime. |
| RenewalPricingType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The price used when renewing a subscription. Its UI label is Pricing Type for Renewal. This field is available in API version 55.0 and later. This field is available when Revenue Cloud is enabled.  Possible values are:  - `LastNegotiatedPrice` - `ListPrice` |
| RenewalTerm | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  With Renewal Term Unit, defines the default subscription term for renewal quotes. This field is available in API version 55.0 and later. This field is available when Revenue Cloud is enabled. |
| RenewalTermUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit of time for a subscription term. This field is available in API version 55.0 and later. This field is available when Revenue Cloud is enabled.  Possible values are:  - `Annual`—Available in API version   58.0 and later. —UI label is `Years`. - `Months` |
| SalesStoreId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the RetailStore or WebStore associated with this Asset.  This field is a polymorphic relationship field.  To access this field, your org must have a Salesforce Order Management license or a B2B Commerce License.  This field is available in API v60.0 and later.  Relationship Name  SalesStore  Relationship Type  Lookup  Refers To  RetailStore, WebStore |
| SerialNumber | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Serial number for this asset. |
| State | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The state detail for the address. |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Customizable picklist of values. The default picklist includes the following values:  - `Purchased` - `Shipped` - `Installed` - `Registered` - `Obsolete` |
| StatusReason | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The explanation of the device status. This field is available from API version 49.0 and later.  Possible values are:  - `Not   Ready` - `Off` - `Offline` - `Online` - `Paused` - `Standby` |
| StockKeepingUnit | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The SKU assigned to the related product. |
| Street | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The street detail for the address. |
| SumDowntime | Type  double  Properties  Filter, Nillable, Sort  Description  Accumulated downtime (planned and unplanned), determined as follows:  - When only UptimeRecordStart   is set, the sum of all downtime from   UptimeRecordStart - When UptimeRecordStart and   UptimeRecordEnd are set, the   sum of all downtime from   UptimeRecordStart to   UptimeRecordEnd  Otherwise, downtime isn’t accumulated. |
| SumUnplannedDowntime | Type  double  Properties  Filter, Nillable, Sort  Description  Accumulated unplanned downtime, determined as follows:  - When only UptimeRecordStart   is set, the sum of all unplanned downtime from   UptimeRecordStart - When UptimeRecordStart and   UptimeRecordEnd are set, the   sum of all unplanned downtime from   UptimeRecordStart to   UptimeRecordEnd  Otherwise, unplanned downtime isn’t accumulated. |
| TotalLifecycleAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount of revenue for the asset, including revenue from each stage in the asset lifecycle. This field is available when CPQ Plus, Salesforce Billing, or Revenue Cloud is enabled. |
| UptimeRecordEnd | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date until which SumDowntime and SumUnplannedDowntime are accumulated. |
| UptimeRecordStart | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date from which SumDowntime and SumUnplannedDowntime are accumulated. |
| UsageEndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Date when usage for this asset ends or expires. |
| Uuid | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique ID for the asset. This field is available in API version 49.0 and later. |

## Usage

Use this object to track products sold to customers. With asset tracking, a client
application can quickly determine which products were previously sold or are
currently installed at a specific account. You can also create hierarchies of up to
10,000 assets.

For example, suppose that your company wants to renew and upsell opportunities on
products sold in the past. Similarly, your company can track competitive products in
a customer environment where products can be replaced or swapped out.

Asset tracking is also useful for product support, providing detailed information to
assist with product-specific support issues. For example, the
PurchaseDate or SerialNumber can
indicate whether a given product has certain maintenance requirements, including
product recalls. Similarly, the UsageEndDate can indicate when
the asset was removed from service or when a license or warranty expires.

If an application creates an Asset record, it must specify a
Name and either an AccountId,
ContactId, or both.

With REST API, use the `getRelatedListInfo` function to get
information about related lists on the asset. Note that when requesting information
about `PrimaryAssets`, the response is labeled `Related Assets`, and the response for
`RelatedAssets` is labeled `Primary
Assets`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
those objects are available in the same API versions as this object. Otherwise,
they’re available in the specified API version and later.

[AssetChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm "HTML (New Window)") (API version 44.0)
:   Change events are available for the object.

[AssetFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssetHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssetOwnerSharingRule](./sforce_api_objects_assetownersharingrule.htm.md "Represents the rules for sharing an Asset with users other than the owner. This object is available in API version 33.0 and later.")
:   Sharing rules are available for the object.

[AssetShare](./sforce_api_objects_assetshare.htm.md "Represents a sharing entry on an Asset. This object is available in API version 33.0 and later.")
:   Sharing is available for the object.
