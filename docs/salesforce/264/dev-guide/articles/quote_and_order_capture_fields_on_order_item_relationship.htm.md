---
page_id: quote_and_order_capture_fields_on_order_item_relationship.htm
title: Transaction Management Fields on Order Item Relationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_item_relationship.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-11-23
---

# Transaction Management Fields on Order Item Relationship

Standard and custom fields extend the standard Order Item Relationship object for use in Transaction Management. This object is available in API version 58.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Item Relationship](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_orderitemrelationship.htm) for fields on the platform object.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_item_relationship.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
