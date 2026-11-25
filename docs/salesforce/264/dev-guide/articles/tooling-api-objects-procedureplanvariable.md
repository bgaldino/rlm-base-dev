---
page_id: tooling-api-objects-procedureplanvariable
title: ProcedurePlanVariable
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplanvariable.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-tooling-api-parent
legacy_page_id: tooling_api_objects_procedureplanvariable.htm
fetched_at: 2026-11-25
---

# ProcedurePlanVariable

Represents the setup for any adhoc user-defined variable that can be linked to a procedure plan definition record. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DataType

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The data type of the input procedure plan variable.

### DefaultValue

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The default value for the user-defined procedure plan variable.

### DeveloperName

**Type:** string

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The unique name of the procedure plan variable record.

This name must begin with a letter and use only alphanumeric characters and underscores. It can’t include spaces, end with an underscore, or have two consecutive underscores.

### Label

**Type:** string

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The label of the procedure plan variable.

### ProcedurePlanVersionId

**Type:** reference

**Properties:** Create, Filter, Group, Sort

**Description:** The procedure plan version associated with the procedure plan variable record.

This field is a relationship field.

**Relationship Name:** ProcedurePlanVersion

**Relationship Type:** Master-detail

**Refers To:** ProcedurePlanDefinitionVersion (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplanvariable.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
