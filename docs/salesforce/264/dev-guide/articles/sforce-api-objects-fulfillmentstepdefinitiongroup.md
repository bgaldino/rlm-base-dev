---
page_id: sforce-api-objects-fulfillmentstepdefinitiongroup
title: FulfillmentStepDefinitionGroup
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepdefinitiongroup.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentstepdefinitiongroup.htm
fetched_at: 2026-11-25
---

# FulfillmentStepDefinitionGroup

Represents a set of fulfillment step definitions. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user referenced this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user viewed this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the fulfillment step definition group.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### UsageType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The business that uses Fulfillment Orchestration.

Possible values are `IntegrationOrchestrator`, `Generic`, or `InsuranceRuleAction`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentStepDefinitionGroupHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[FulfillmentStepDefinitionGroupShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentstepdefinitiongroup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
