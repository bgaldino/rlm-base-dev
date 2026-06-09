---
page_id: billing_sforce_api_objects_collectionplanitem.htm
title: Billing Fields on CollectionPlanItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_collectionplanitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on CollectionPlanItem

Standard fields extend the CollectionPlanItem object for use in Billing to
represent information about the invoice balance. This object is available in API
version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Collections and Recovery
Specialist permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| InvoiceBalance | Type  currency  Properties  Filter, Nillable, Sort  Description  The balance amount of the invoice associated with the collection plan item. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[CollectionPlanItemChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.")
:   Change events are available for the object.

[CollectionPlanItemFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CollectionPlanItemHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object

#### See Also

- [*Industries Common Resources Developer Guide*: CollectionPlanItem](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/sforce_api_objects_collectionplanitem.htm "Industries Common Resources Developer Guide: CollectionPlanItem - HTML (New Window)")
