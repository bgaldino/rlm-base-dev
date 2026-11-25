---
page_id: tooling-api-objects-procedureplandefinitionversion
title: ProcedurePlanDefinitionVersion
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplandefinitionversion.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-tooling-api-parent
legacy_page_id: tooling_api_objects_procedureplandefinitionversion.htm
fetched_at: 2026-11-25
---

# ProcedurePlanDefinitionVersion

Represents the versions for a procedure plan definition. Multiple versions under a procedure plan definition must be active at a time, which can be resolved at run time using the rank field. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextDefinition

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The context definition associated with the procedure plan definition record.

Valid values are:

- `11ODU00000007Zx2AI`

- `11ODU000000084F2AQ`

- `CollectionPlanEvent__stdctx`

- `CommerceCartContextDefinition__stdctx`

- `SalesTransactionContext__stdctx`

- `TestContextService__stdctx`

- `TestDynamicAttribute__stdctx`

- `TestExtendedDefinition__stdctx`

### DefaultReadContextMapping

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The default read context mapping used to read from the mapped object and populate the context definition.

### DefaultSaveContextMapping

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The save context mapping used to save from the context definition and populate the mapped object.

### DeveloperName

**Type:** string

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The unique name of the procedure plan definition version record.

This name must begin with a letter and use only alphanumeric characters and underscores. It can’t include spaces, end with an underscore, or have two consecutive underscores.

### EffectiveFrom

**Type:** dateTime

**Properties:** Create, Filter, Sort, Update

**Description:** The date and time when the procedure plan definition comes into effect.

### EffectiveTo

**Type:** dateTime

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The date and time when the procedure plan definition is no longer in effect.

### InheritedFrom

**Type:** string

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort

**Description:** The template from which this procedure plan definition is created.

### IsActive

**Type:** boolean

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

**Description:** Indicates if this procedure plan definition version is active ( `true`) or not ( `false`).

The default value is `false`.

### ProcedurePlanDefinitionId

**Type:** reference

**Properties:** Create, Filter, Group, Sort

**Description:** The procedure plan definition associated with this procedure plan definition version record.

This field is a relationship field.

**Relationship Name:** ProcedurePlanDefinition

**Relationship Type:** Master-detail

**Refers To:** ProcedurePlanDefinition (the master object)

### Rank

**Type:** int

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The current rank of the procedure plan definition version that’s used to determine which procedure plan definition version is executed .

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplandefinitionversion.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
