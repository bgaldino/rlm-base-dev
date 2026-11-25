---
page_id: quote-and-order-capture-fields-on-object-state-transition
title: Transaction Management Fields on Object State Transition
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-object-state-transition.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-fields-on-standard-objects
legacy_page_id: quote_and_order_capture_fields_on_object_state_transition.htm
fetched_at: 2026-11-25
---

# Transaction Management Fields on Object State Transition

Standard and custom fields extend the standard Object State Transition object for use in Transaction Management to define the valid transition between two statuses. This object is available in API version 60.0 and later.

## CustomPermissionId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The ID of the associated custom permission.

This field is a relationship field.

**Relationship Name:** CustomPermission

**Relationship Type:** Lookup

**Refers To:** CustomPermission

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-object-state-transition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
