---
page_id: sforce_api_objects_pricebookentry.htm
title: PriceBookEntry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricebookentry.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PriceBookEntry

Represents a product entry (an association between a Pricebook2 and Product2)
in a price book. This object is available in API version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Fields

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Salesforce Object Search Language (SOSL) allows you to search
records across standard and custom objects. When filtering records in the PriceBookEntry
object using SOSL, you can only sort by fields related to Product2.

| Field | Details |
| --- | --- |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Available only for organizations with the multicurrency feature enabled. Contains the ISO code for any currency allowed by the organization.  Possible values are:  - `BHD`—Bahraini Dinar - `JPY`—Japanese Yen - `USD`—U.S. Dollar  The default value is `USD`. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this price book entry is active (true) or not (false). Although you can never delete PricebookEntry records, your client application can set this flag to false. Inactive PricebookEntry records are hidden in many areas in the user interface. You can change this flag on a PricebookEntry record as often as necessary.  The default value is `false`. |
| IsArchived | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the PricebookEntry has been archived (true) or not (false). This field is set to true when the Product2 record it’s associated with is archived, or when the Pricebook2 record is archived. This field is read only.  The default value is `false`. |
| Name | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Name of this price book entry record. This read-only field references the value in the Name field of the Product2 record. |
| Pricebook2Id | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. ID of the Pricebook2 record with which this record is associated. This field must be specified when creating Pricebook2 records. It can’t be changed in an update.  This field is a relationship field.  Relationship Name  Pricebook2  Relationship Type  Lookup  Refers To  Pricebook2 |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. ID of the Product2 record with which this record is associated. This field must be specified when creating Product2 records. It can’t be changed in an update.  This field is a relationship field.  Relationship Name  Product2  Relationship Type  Lookup  Refers To  Product2 |
| ProductCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Product code for this record. This read-only field references the value in the ProductCode field of the associated Product2 record. |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the related product selling model.  This field is a relationship field.  Relationship Name  ProductSellingModel  Relationship Type  Lookup  Refers To  ProductSellingModel |
| UnitPrice | Type  currency  Properties  Create, Filter, Sort, Update  Description  Required. Unit price for this price book entry. You can specify a value only if UseStandardPrice is set to false. |
| UseStandardPrice | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this price book entry uses the standard price defined in the standard Pricebook2 record (true) or not (false). If set to true, then the UnitPrice field is read-only, and the value is the same as the UnitPrice value in the corresponding PricebookEntry in the standard price book (that is, the PricebookEntry record whose Pricebook2Id refers to the standard price book and whose Product2Id and CurrencyIsoCode are the same as this record). For PricebookEntry records associated with the standard Pricebook2 record, this field must be set to true.  The default value is `false`. |

## Usage

Use this object to define the association between your
organization’s products (Product2) and your organization’s standard price book or to
custom price books ( Pricebook2). Create one PricebookEntry record for each standard or
custom price and currency combination for a product in a Pricebook2.

When creating
these records, you must specify the IDs of the associated Pricebook2 record and Product2
record. Once these records are created, your client application can’t update these
IDs.

This object is defined only for those organizations that have products
enabled as a feature. If the organization doesn’t have the products feature enabled,
then the PricebookEntry object doesn’t appear in the describeGlobal call, and you can’t
access it.

If you delete a PriceBookEntry that is referenced by a line item, the
line item is unaffected, but the PriceBookEntry is archived and unavailable from the
API. Deleted PriceBookEntry records can’t be recovered.

You must load the standard
price for a product before you’re permitted to load its custom prices.

Create
PriceBookEntry records by using this sObject
API.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/PricebookEntry
```

This
example shows a sample request that specifies the details of a price book
entry.

```
{
  "ProductSellingModelId": "0jPxx0000000005EAA",
  "Product2Id": "01tLT00000A0YTlYAN",
  "IsActive": true,
  "Pricebook2Id": "01s1W000000SYXNQA4",
  "UnitPrice": "100.00"
}
```

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PriceBookEntryChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.")
:   Change events are available for the object.

[PriceBookEntryHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
