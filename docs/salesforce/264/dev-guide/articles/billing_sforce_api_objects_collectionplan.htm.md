---
page_id: billing_sforce_api_objects_collectionplan.htm
title: Billing Fields on CollectionPlan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_collectionplan.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-11-23
---

# Billing Fields on CollectionPlan

Standard fields extend the CollectionPlan object for use in Billing to represent information about the total invoice balance. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Collections and Recovery Specialist permission set to access this object.

#### See Also

- [*Industries Common Resources Developer Guide*: CollectionPlan](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_objects_collectionplan.htm "Industries Common Resources Developer Guide: CollectionPlan - HTML (New Window)")

## Fields

### TotalInvoiceBalance

**Type:** currency

**Properties:** Filter, Nillable, Sort

**Description:** The sum of all invoice balances for collection plan items associated with the collection plan.

### OverdueRiskIndicator

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** Indicates the overdue risk level for the collection plan. Available in API version 67.0 and later.

Valid values are:

- `Low`
- `Medium`
- `High`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[CollectionPlanChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events."):** Change events are available for the object.

**[CollectionPlanFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object."):** Feed tracking is available for the object.

**[CollectionPlanHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

**[CollectionPlanShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object."):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_collectionplan.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
