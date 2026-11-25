---
page_id: sforce-api-objects-fulfillmentassetstateperiod
title: FulfillmentAssetStatePeriod
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetstateperiod.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentassetstateperiod.htm
fetched_at: 2026-11-25
---

# FulfillmentAssetStatePeriod

Represents the period during which the fulfillment asset configuration is applicable. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**:

Possible values are:

- `EUR`—Euro

- `INR`—Indian Rupee

- `USD`—U.S. Dollar

The default value is `USD`.

### EndTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Represents the end time of the state period. If null, the configuration is effective from Start Time. If Start Time is also null, the configuration is effective at all times.

### FulfillmentAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Represents the fulfillment asset to which this fulfillment asset state period applies.

This field is a relationship field.

- **Relationship Name**: FulfillmentAsset

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentAsset (the master object)

### IsSuperseded

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates if the state period is superseded and the record is replaced by a newer version due to updates by the fulfillment process.

The default value is `false`.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the fulfillment asset state period.

### Quantity

- **Type**: double

- **Properties**: Create, Filter, Sort, Update

- **Description**: Represents the fulfillment product quantity applicable for the state period.

### StartTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Represents the start time of the state period. If null, the configuration is effective until End Time. If End Time is also null, the configuration is effective at all times.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetstateperiod.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
