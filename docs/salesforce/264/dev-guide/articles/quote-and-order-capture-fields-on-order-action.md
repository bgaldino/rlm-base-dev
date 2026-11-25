---
page_id: quote-and-order-capture-fields-on-order-action
title: Transaction Management Fields on Order Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-order-action.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-fields-on-standard-objects
legacy_page_id: quote_and_order_capture_fields_on_order_action.htm
fetched_at: 2026-11-25
---

# Transaction Management Fields on Order Action

Standard and custom fields extend the standard Order Action object for use in Transaction Management. This object is available in API version 55.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Action](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_orderaction.htm) for fields on the Salesforce platform object.

## Fields

### Type

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The business action that created the order product.

Valid values are:

- `Add`

- `Amend`

- `Cancel`

- `No Change`—A child product was added to the bundle, but the top-level product in the bundle was otherwise unchanged.

- `Renew`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-order-action.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
