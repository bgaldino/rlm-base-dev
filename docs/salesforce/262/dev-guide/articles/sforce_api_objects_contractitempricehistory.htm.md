---
page_id: sforce_api_objects_contractitempricehistory.htm
title: ContractItemPriceHistory
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_contractitempricehistory.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# ContractItemPriceHistory

Represents the history of changes to the values in the fields of a
ContractItemPrice object. This object is available in API version 61.0 and
later.

## Supported Calls

`describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`

## Special Access Rules

This object is available in Enterprise, Unlimited, and Developer Editions of Revenue
Cloud.

## Fields

| Field | Details |
| --- | --- |
| ContractItemPriceId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the ContractItemPrice record.  This field is a relationship field.  Relationship Name  ContractItemPrice  Relationship Type  Lookup  Refers To  ContractItemPrice |
| DataType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Data type of the field that was changed.  Valid values are:  - `Address` - `AnyType` - `AutoNumber` - `Base64` - `BitVector` - `Boolean` - `Content` - `Currency` - `DataCategoryGroupReference` - `DateOnly` - `DateTime` - `Division` - `Double` - `DynamicEnum` - `Email` - `EncryptedBase64` - `EncryptedText` - `EntityId` - `EnumOrId` - `ExternalId` - `Fax` - `File` - `HtmlMultiLineText` - `HtmlStringPlusClob` - `InetAddress` - `Json` - `Location` - `MultiEnum` - `MultiLineText` - `Namespace` - `Percent` - `PersonName` - `Phone` - `Raw` - `RecordType` - `SfdcEncryptedText` - `SimpleNamespace` - `StringPlusClob` - `Switchable_PersonName` - `Text` - `TimeOnly` - `Url` - `YearQuarter` |
| Field | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Name of the field that was changed.  Possible values are:  - `AdjustmentMethod` - `Contract` - `DiscountType` - `DiscountValue` - `EndDate` - `Item` - `Name` - `Price` - `ProductSellingModel` - `StartDate` - `created` - `customPersonMerged` - `feedEvent` - `individualMerged` - `locked`—Record   locked. - `ownerAccepted`—Owner (Accepted) - `ownerAssignment`—Owner (Assignment) - `unlocked`—Record   unlocked. |
| NewValue | Type  anyType  Properties  Nillable, Sort  Description  New value of the field that was changed. |
| OldValue | Type  anyType  Properties  Nillable, Sort  Description  Latest value of the field before it was changed. |
