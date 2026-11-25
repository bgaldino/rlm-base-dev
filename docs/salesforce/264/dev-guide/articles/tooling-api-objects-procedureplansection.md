---
page_id: tooling-api-objects-procedureplansection
title: ProcedurePlanSection
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplansection.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-tooling-api-parent
legacy_page_id: tooling_api_objects_procedureplansection.htm
fetched_at: 2026-11-25
---

# ProcedurePlanSection

Represents various procedure setup sections for a procedure plan definition. Each section enables the setup of a procedure of a type that can be further determined by using a rule-based criteria or it can be set based on a selected lookup table. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### Description

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The description of the procedure plan section.

### IsInherited

**Type:** boolean

**Properties:** Create, Defaulted on create, Filter, Group, Sort

**Description:** Indicates if the section is inherited from a template ( `true`) ot not ( `false`).

The default value is `false`.

### Phase

**Type:** string

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The phase associated with the procedure plan section record.

### ProcedurePlanVersionId

**Type:** reference

**Properties:** Create, Filter, Group, Sort

**Description:** The procedure plan version associated with this procedure plan section record.

This field is a relationship field.

**Relationship Name:** ProcedurePlanVersion

**Relationship Type:** Master-detail

**Refers To:** ProcedurePlanDefinitionVersion (the master object)

### ResolutionType

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The type of resolution used to filter the procedure.

Valid values are `Default` or `RuleBased`

### SectionType

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort

**Description:** The type of procedure section.

Valid values are `Custom`, `PricingDiscoveryProcedure`, `PricingProcedure`, or `ProductDiscoveryProcedure`

### Sequence

**Type:** int

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The sequence in which the procedures are processed.

### SubSectionType

**Type:** string

**Properties:** Create, Filter, Group, Sort

**Description:** The procedure subsection added to the procedure plan definition.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplansection.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
