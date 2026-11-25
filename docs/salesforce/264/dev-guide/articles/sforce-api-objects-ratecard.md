---
page_id: sforce-api-objects-ratecard
title: RateCard
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratecard.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_ratecard.htm
fetched_at: 2026-11-25
---

# RateCard

Represents the rules used to rate the consumption of a group of resources within a product. Usage of a resource is billed at a specified rate if the user consumes more than their allowance for a time period. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Description about the rate card.

### EffectiveFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: Date and time when the rate card becomes effective.

### EffectiveTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Date and time until when the rate card remains effective.

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

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Name of the rate card.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### Type

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Type of rate card.

Valid values are `Attribute`, `Base`, or `Tier`.

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[RateCardFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[RateCardHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[RateCardShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratecard.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
