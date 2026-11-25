---
page_id: sforce-api-objects-pricebookratecard
title: PriceBookRateCard
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebookratecard.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_pricebookratecard.htm
fetched_at: 2026-11-25
---

# PriceBookRateCard

Represents a junction between price book and rate card objects. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Auto-generated identifier for the price book rate card record.

### PriceBookId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Price book ID that’s associated with the rate cards IDs. For Quote, Order, and Contracts, the price book IDs identify the associated rate cards.

This field is a relationship field.

- **Relationship Name**: PriceBook

- **Relationship Type**: Master-detail

- **Refers To**: Pricebook2 (the master object)

### RateCardId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Rate card ID that’s associated with the price book.

This field is a relationship field.

- **Relationship Name**: RateCard

- **Relationship Type**: Master-detail

- **Refers To**: RateCard (the detail object)

### RateCardType

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Type of rate card associated with the price book.

Valid values are `Attribute`, `Base`, or `Tier`.

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PriceBookRateCardFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[PriceBookRateCardHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebookratecard.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
