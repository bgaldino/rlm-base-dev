---
page_id: billing-sforce-api-objects-collectionplanitem
title: Billing Fields on CollectionPlanItem
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-collectionplanitem.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-extended-standard-object-fields
legacy_page_id: billing_sforce_api_objects_collectionplanitem.htm
fetched_at: 2026-11-25
---

# Billing Fields on CollectionPlanItem

Standard fields extend the CollectionPlanItem object for use in Billing to represent information about the invoice balance. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Collections and Recovery Specialist permission set to access this object.

**See Also**

- [*Industries Common Resources Developer Guide*: CollectionPlanItem](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_collectionplanitem.htm)

## Fields

### InvoiceBalance

**Type:** currency

**Properties:** Filter, Nillable, Sort

**Description:** The balance amount of the invoice associated with the collection plan item.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[CollectionPlanItemChangeEvent](./sforce-api-associated-objects-change-event.md):** Change events are available for the object.

**[CollectionPlanItemFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[CollectionPlanItemHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-collectionplanitem.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
