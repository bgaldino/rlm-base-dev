---
page_id: sforce-api-objects-contractitemprice
title: ContractItemPrice
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-contractitemprice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_contractitemprice.htm
fetched_at: 2026-11-25
---

# ContractItemPrice

Represents an object that’s used to capture a price for a product on a contract. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

This object is available in Enterprise, Unlimited, and Developer Editions of Revenue Cloud.

## Fields

### AdjustmentMethod

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Method used to apply discount.

Valid values are:

- `Range`—Apply the discount to all items after you reach the discount tier. For example, suppose that you give a 10% discount for 50 or more items. If a customer orders 50 products, and the type is `range`, apply the 10% discount to all 50 items.

- `Slab`—Apply discounts in tiers. For example, suppose that you order 30 products, and the type is `slab`, you can apply a 10% discount to units 1–9, a 20% discount to units 10–19, and a 30% discount to units 20–30.

### ContractId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: ID of the contract.

This field is a relationship field.

- **Relationship Name**: Contract

- **Relationship Type**: Master-detail

- **Refers To**: Contract (the master object)

### DiscountType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The type of discount applied, a percentage of the price or an amount.

Valid values are `AdjustmentAmount` or `AdjustmentPercentage`.

### DiscountValue

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The value of the discount applied, based on the discount type.

### EndDate

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: End date and time of the relationship between the contract and contract item price.

### ItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: ID of the product or product category related to a price in a contract.

This field is a polymorphic relationship field.

- **Relationship Name**: Item

- **Relationship Type**: Lookup

- **Refers To**: Product2, ProductCategory

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp when the current user last accessed this record, a record related to this record, or a list view.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp when the current user last viewed this record or list view. If this value is null, the user accessed this record or list view (`LastReferencedDate`) but didn’t view it.

### ListPrice

- **Type**: currency

- **Properties**: Filter, Nillable

- **Description**: The list price of the product. This value is read-only and inherited from the price book related to the contract when the contract item price is created. Use the list price to compare the advertised price to prices that customers receive during contract negotiations. This field is available in API version 66.0 and later.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Auto-generated number assigned to the contract item price. (Read only)

### Price

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Unit price for the product sold as part of the contract.

### ProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Product selling model for the product associated with the price.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

### SellingModelType

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Selling mode type to specify whether the product sold is a one-time sale, an evergreen subscription, or a subscription with a defined term.

Valid values are `Evergreen`, `OneTime`, or `TermDefined`.

The value derived from the product selling model.

### StartDate

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: Start date and time of the relationship between the contract and contract item price.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ContractItemPriceHistory](./sforce-api-objects-contractitempricehistory.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-contractitemprice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
