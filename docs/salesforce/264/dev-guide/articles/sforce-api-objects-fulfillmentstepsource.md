---
page_id: sforce-api-objects-fulfillmentstepsource
title: FulfillmentStepSource
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepsource.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentstepsource.htm
fetched_at: 2026-11-25
---

# FulfillmentStepSource

Represents a link between a fulfillment step and the corresponding order lines. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: An automatically generated name for the fulfillment step source.

### SourceIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The identifier of the source order line item (order item or fulfillment order line).

### SourceLineItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: For internal use only.

This field is a polymorphic relationship field.

- **Relationship Name**: SourceLineItem

- **Refers To**: FulfillmentOrderLineItem, OrderItem

### StepId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The identifier of the fulfillment step.

This field is a relationship field.

- **Relationship Name**: Step

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentStep (the master object)

### VersionGroupIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the version group that’s assigned to the fulfillment step source item.This field is available in API version 64.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentStepSourceChangeEvent](./sforce-api-associated-objects-change-event.md):** Change events are available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepsource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
