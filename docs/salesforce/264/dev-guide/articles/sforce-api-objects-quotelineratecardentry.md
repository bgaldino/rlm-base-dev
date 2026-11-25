---
page_id: sforce-api-objects-quotelineratecardentry
title: QuoteLineRateCardEntry
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotelineratecardentry.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_quotelineratecardentry.htm
fetched_at: 2026-11-25
---

# QuoteLineRateCardEntry

Represents the catalog and negotiated rates of a usage resource associated with a quote line item that’s used to charge overage consumption. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

### IsChosenRate

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether this rate is the chosen rate for the associated binding target and usage resource (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: An auto-generated number assigned to the quote line rate card entry record.

### NegotiatedRate

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The base negotiated rate used to charge overage consumption.

### QuoteLineItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The parent quote line item associated with the quote line rate card entry.

This field is a relationship field.

- **Relationship Name**: QuoteLineItem

- **Relationship Type**: Master-detail

- **Refers To**: QuoteLineItem (the master object)

### RateCardEntryId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The rate card entry containing catalog rates that’s associated with the quote line rate card entry.

This field is a relationship field.

- **Relationship Name**: RateCardEntry

- **Refers To**: RateCardEntry

### RateCardId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The rate card associated with the quote line rate card entry.

This field is a relationship field.

- **Relationship Name**: RateCard

- **Refers To**: RateCard

### RateUnitOfMeasureId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The standard unit of measure containing the unit for the negotiated rate that’s associated with the quote line rate card entry.

This field is a relationship field.

- **Relationship Name**: RateUnitOfMeasure

- **Refers To**: UnitOfMeasure

### UsageResourceId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The usage resource associated with the quote line rate card entry.

This field is a relationship field.

- **Relationship Name**: UsageResource

- **Refers To**: UsageResource

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotelineratecardentry.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
