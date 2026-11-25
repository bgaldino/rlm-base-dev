---
page_id: sforce-api-objects-pricebook2
title: PriceBook2
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebook2.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_pricebook2.htm
fetched_at: 2026-11-25
---

# PriceBook2

Represents a price book that contains the list of products that your org sells. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization. Possible values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar The default value is `USD`.

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Text description of the price book.

### IsActive

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the price book is active (true) or not (false). Inactive price books are hidden in many areas in the user interface. You can change this field’s value as often as necessary. Label is **Active**. The default value is `false`.

### IsArchived

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the price book has been archived (true) or not (false). This field is read only. The default value is `false`.

### IsStandard

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the price book is the standard price book for the org (true) or not (false). Every org has one standard price book—all other price books are custom price books. The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. Name of this object. This field is read-only for the standard price book.

### ValidFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when a price book is initially valid. If this field is null, the price book is valid immediately when active.

### ValidTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when a price book is valid to. If this field is null, the price book is valid until it’s deactivated.

## Usage

A price book is a list of products that your org sells.

- 

Each org has one standard price book that defines the standard or generic list price for each product or service that it sells.

- 

An org can have multiple custom price books to use for specialized purposes, such as for discounts, different channels or markets, or select accounts or opportunities. While your client application can create, delete, and update custom price books, your client application can only update the standard price book.

- 

For some orgs, the standard price book is the only price needed. If you set up other price books, you can reference the standard price book when setting up list prices in custom price books.

Use this object to query standard and custom price books that have been configured for your org. A common use of this object is to allow your client application to obtain valid Pricebook2 object IDs for use when configuring PricebookEntry records via the API.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

[PriceBook2ChangeEvent](./sforce-api-associated-objects-change-event.md): Change events are available for the object.

[PriceBook2History](./sforce-api-associated-objects-history.md): History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebook2.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
