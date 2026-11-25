---
page_id: sforce-api-objects-fulfillmentstepjeopardyrule
title: FulfillmentStepJeopardyRule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepjeopardyrule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentstepjeopardyrule.htm
fetched_at: 2026-11-25
---

# FulfillmentStepJeopardyRule

Represents the duration and tolerance for the step in the fulfillment process to allow the overall tracking of rules and risks. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### EstimatedDuration

- **Type**: int

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The estimated time to complete the fulfillment step.

### EstimatedDurationUnit

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The unit of measurement that applies to the estimated time to complete the fulfillment step.

Valid values are `Days`, `Hours`, `Minutes`, or `Seconds`.

The default value is `Minutes`.

### FlowDefinition

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The flow definition that’s associated with the `AutoTask` type of the fulfillment step.

### IntegrationDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The integration definition that’s associated with the `Callout` type of the fulfillment step.

This field is a relationship field.

- **Relationship Name**: IntegrationDefinition

- **Relationship Type**: Lookup

- **Refers To**: IntegrationProviderDef

### JeopardyThreshold

- **Type**: int

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The value indicating the threshold after which the fulfillment step is in jeopardy.

### JeopardyThresholdUnit

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The unit of measurement that applies to the jeopardy threshold value.

Valid values are `Days`, `Hours`, `Minutes`, or `Seconds`.

The default value is `Minutes`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: For internal use only.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: For internal use only.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: For internal use only.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: For internal use only.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### StepType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of fulfillment step that’s affected by the jeopardy rule.

Valid values are `AutoTask`, `Callout`, `ManualTask`, `Milestone`, or `Pause`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepjeopardyrule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
