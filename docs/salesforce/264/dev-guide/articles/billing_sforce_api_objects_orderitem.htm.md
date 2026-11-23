---
page_id: billing_sforce_api_objects_orderitem.htm
title: Billing Fields on OrderItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_orderitem.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-11-23
---

# Billing Fields on OrderItem

Standard fields extend the OrderItem object for use in Billing to represent information about the billing term.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Admin permission set or the Billing Operations User permission set to access this object.

#### See Also

- [*Object Reference for the Salesforce Platform*: OrderItem](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_orderitem.htm)

## Fields

### BillingReference2

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The reference to the original order item for which this amend, renew, or cancel record is created.

### BillingTreatmentId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The reference to the billing treatment.

This field is a relationship field.

**Relationship Name:** BillingTreatment

**Refers To:** BillingTreatment

### BillingTerm

**Type:** int

**Properties:** Defaulted on create, Filter, Group, Nillable, Sort

**Description:** The number of billing frequency units to combine into a billing period item. Available in API version 68.0 and later.

### LegalEntityId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The reference to the legal entity.

This field is a relationship field.

**Relationship Name:** LegalEntity

**Refers To:** LegalEntity

### NetUnitPrice

**Type:** currency

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The net unit price of the related order item. Available in API version 64.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn't specified, they're available in the same API versions as this object. Otherwise, they're available in the specified API version and later.

**[OrderItemChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events."):** Change events are available for the object.

**[OrderItemFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object."):** Feed tracking is available for the object.

**[OrderItemHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_orderitem.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
