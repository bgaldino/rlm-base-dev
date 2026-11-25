---
page_id: quote-and-order-capture-fields-on-order-item-relationship
title: Transaction Management Fields on Order Item Relationship
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-order-item-relationship.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-fields-on-standard-objects
legacy_page_id: quote_and_order_capture_fields_on_order_item_relationship.htm
fetched_at: 2026-11-25
---

# Transaction Management Fields on Order Item Relationship

Standard and custom fields extend the standard Order Item Relationship object for use in Transaction Management. This object is available in API version 58.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Item Relationship](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_orderitemrelationship.htm) for fields on the platform object.

## Fields

### ProductRelatedComponentId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort

**Description:** The ID of the product that is included in a product bundle, a set, or a product and an add-on.

This field is a relationship field.

**Relationship Name:** ProductRelatedComponent

**Relationship Type:** Lookup

**Refers To:** ProductRelatedComponent

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-order-item-relationship.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
