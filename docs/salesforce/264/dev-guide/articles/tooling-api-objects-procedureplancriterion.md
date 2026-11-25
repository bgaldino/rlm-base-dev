---
page_id: tooling-api-objects-procedureplancriterion
title: ProcedurePlanCriterion
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplancriterion.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-tooling-api-parent
legacy_page_id: tooling_api_objects_procedureplancriterion.htm
fetched_at: 2026-11-25
---

# ProcedurePlanCriterion

Represents a criterion within a procedure plan option record. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ActualValue

**Type:** string

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The user-defined value that’s compared to the value of the sObject field value.

### DataType

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The data type of the field from the selected object.

### FieldPath

**Type:** string

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The path of the field used in a procedure in relation to the object that the field belongs to.

### ObjectField

**Type:** string

**Properties:** Create, Filter, Group, Sort, Update

**Description:** The Salesforce object field value used to resolve the procedure plan option.

### Operator

**Type:** picklist

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

**Description:** The operator used by the procedure plan criterion.

Valid values are:

- `Equals`

- `GreaterThan`

- `GreaterThanOrEquals`

- `In`

- `IsNotNull`

- `IsNull`

- `LessThan`

- `LessThanOrEquals`

- `NotEquals`

- `NotIn`

### ProcedurePlanOptionId

**Type:** reference

**Properties:** Create, Filter, Group, Sort

**Description:** The procedure plan option associated with the procedure plan criterion record.

This field is a relationship field.

**Relationship Name:** ProcedurePlanOption

**Relationship Type:** Master-detail

**Refers To:** ProcedurePlanOption (the master object)

### Sequence

**Type:** int

**Properties:** Create, Filter, Group, Sort

**Description:** The sequence in which the conditions defined in the procedure plan criteria are processed.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/tooling-api-objects-procedureplancriterion.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
