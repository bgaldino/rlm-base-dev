---
page_id: quote_and_order_capture_fields_on_object_state_definition.htm
title: Transaction Management Fields on Object State Definition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_object_state_definition.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-11-23
---

# Transaction Management Fields on Object State Definition

Standard and custom fields extend the standard Object State Definition object for use in Transaction Management to represent the object state model for a particular status field for an entity.  This object is available in API version 60.0 and later.

## AppUsageType

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** This field indicates under which AppUsageType the transition applies
to. For example, ObjectStateDefinition associated with “Revenue Lifecycle Management”
AppUsageType will apply to quotes, assets, or orders associated with “Revenue Lifecycle
Management”.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_object_state_definition.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
