---
page_id: sforce_api_objects_orderitemratecardentry.htm
title: OrderItemRateCardEntry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_orderitemratecardentry.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-11-23
---

# OrderItemRateCardEntry

Represents the catalog and negotiated rates of a usage metric associated with an order item that's used to charge overage consumption. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

## Fields

### IsChosenRate

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether this rate is the chosen rate for the associated binding target and usage resource (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later.

### Name

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: An auto-generated number assigned to the order item rate card entry record.

### NegotiatedRate

- **Type**: double
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The base negotiated rate used to charge overage consumption.

### OrderItemId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The parent order item associated with the order item rate card entry.

This field is a relationship field.

- **Relationship Name**: OrderItem
- **Relationship Type**: Master-detail
- **Refers To**: OrderItem (the master object)

### RateCardEntryId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The rate card entry containing catalog rates that's associated with the order item rate card entry.

This field is a relationship field.

- **Relationship Name**: RateCardEntry
- **Refers To**: RateCardEntry

### RateCardId

- **Type**: reference
- **Properties**: Filter, Group, Nillable, Sort
- **Description**: The rate card associated with the order item rate card entry.

This field is a relationship field.

- **Relationship Name**: RateCard
- **Refers To**: RateCard

### RateUnitOfMeasureId

- **Type**: reference
- **Properties**: Filter, Group, Nillable, Sort
- **Description**: The standard unit of measure containing the unit for the negotiated rate that's associated with the order item rate card entry.

This field is a relationship field.

- **Relationship Name**: RateUnitOfMeasure
- **Refers To**: UnitOfMeasure

### UsageResourceId

- **Type**: reference
- **Properties**: Filter, Group, Nillable, Sort
- **Description**: The usage resource associated with the order item rate card entry.

This field is a relationship field.

- **Relationship Name**: UsageResource
- **Refers To**: UsageResource

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_orderitemratecardentry.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
