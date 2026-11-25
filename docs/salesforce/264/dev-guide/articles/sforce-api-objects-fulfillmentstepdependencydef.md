---
page_id: sforce-api-objects-fulfillmentstepdependencydef
title: FulfillmentStepDependencyDef
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepdependencydef.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentstepdependencydef.htm
fetched_at: 2026-11-25
---

# FulfillmentStepDependencyDef

Represents a dependency that must be created between two fulfillment step records. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### CustomScope

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The name of the custom scope when the dependency scope is set to custom. This field is available in API version 68.0 and later.

### DependencyScope

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The scope of the fulfillment step dependency definition. For example, Order or Order Item.

Valid values are:

- `Bundle`

- `LineItem`

- `Plan`

- `CrossPlan`

- `Custom`

The default value is `Plan`.

### DependsOnStepDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The fulfillment step definition that must be executed before this step.

This field is a relationship field.

- **Relationship Name**: DependsOnStepDefinition

- **Refers To**: FulfillmentStepDefinition

### FulfillmentStepDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The identifier of the fulfillment step definition.

This field is a relationship field.

- **Relationship Name**: FulfillmentStepDefinition

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentStepDefinition (the master object)

### IsCompensateInReverse

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the order to insert the compensated group steps is reversed when a fulfillment step is canceled (`true`) or not (`false`).

The default value is `false`. This field is available in API version 63.0 and later.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the fulfillment step dependency definition.

### PropagateStateToDependentStep

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The state that’s propagated to the dependent fulfillment step when the source fulfillment step is amended or canceled in the fulfillment plan.

Valid values are `Amended`, `Both`, `Canceled`, or `None`. This field is available in API version 63.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentStepDependencyDefChangeEvent](./sforce-api-associated-objects-change-event.md):** Change events are available for the object.

**[FulfillmentStepDependencyDefFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[FulfillmentStepDependencyDefHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[FulfillmentStepDependencyDefOwnerSharingRule](./sforce-api-associated-objects-ownersharingrule.md):** Sharing rules are available for the object.

**[FulfillmentStepDependencyDefShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepdependencydef.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
