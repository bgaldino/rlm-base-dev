---
page_id: quote-and-order-capture-fields-on-quote-document
title: Transaction Management Fields on Quote Document
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-quote-document.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-fields-on-standard-objects
legacy_page_id: quote_and_order_capture_fields_on_quote_document.htm
fetched_at: 2026-11-25
---

# Transaction Management Fields on Quote Document

Standard and custom fields extend the standard Quote Document object for use in Transaction Management to represent information about quote documents. This object is available in API version 61.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Quote Document](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_quotedocument.htm) for fields on the Salesforce platform object.

## Fields

### Document Template

**Type:** String

**Properties:** Create, Filter, Group, Nillable, Sort

**Description:** The template ID used for generating the quote document.

### Status

**Type:** Picklist

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** The status of the quote document.

Possible values are:

- `Completed`

- `Failed`

- `Generating`

- `In Progress`

- `None`

- `Queued`

The default value is `None`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-fields-on-quote-document.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
