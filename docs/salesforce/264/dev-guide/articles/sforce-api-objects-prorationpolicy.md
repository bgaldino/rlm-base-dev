---
page_id: sforce-api-objects-prorationpolicy
title: ProrationPolicy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-prorationpolicy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_prorationpolicy.htm
fetched_at: 2026-11-25
---

# ProrationPolicy

Represents the proration policy associated with a Product Selling Model Option that determines how a product’s price is calculated based on subscription duration or billing periods. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Fields

### ArePartialPeriodsAllowed

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether partial periods should be allowed for standard time periods. The default value is false.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the proration policy was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the proration policy was last viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort

- **Description**: The name of the proration policy.

### ProrationPolicyType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort

- **Description**: The type of proration policy to be used. Possible values are `StandardTimePeriods`—Standard Time Periods

### RemainderStrategy

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort

- **Description**: The type of remainder strategy to be used.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-prorationpolicy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
