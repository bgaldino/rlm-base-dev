---
page_id: pricing-sforce-api-objects-indexrate
title: IndexRate
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-sforce-api-objects-indexrate.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-salesforce-pricing-fields-on-standard-objects
legacy_page_id: pricing_sforce_api_objects_indexrate.htm
fetched_at: 2026-11-25
---

# IndexRate

Standard fields extend the IndexRate object for use in Salesforce Pricing to represent information for a given rate. This object is available in API version 65.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### Region

**Type:** picklist

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** Specified the region associated with the given rate.

### UsageType

**Type:** picklist

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** Specifies the usage type associated with the given rate.

Possible values are `Pricing`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-sforce-api-objects-indexrate.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
