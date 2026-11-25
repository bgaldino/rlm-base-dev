---
page_id: sforce-api-objects-expressionset
title: ExpressionSet
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-expressionset.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-standard-objects
legacy_page_id: sforce_api_objects_expressionset.htm
fetched_at: 2026-11-25
---

# ExpressionSet

Represents information about an expression set. An expression set performs a series of calculations using lookups and user-defined variables and constants. This object is available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### ApiName

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The API name of the expression set. This field is unique within your organization. This is a required field.

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The description of the expression set.

### ExecutionScale

- 

**Type**: picklist

- 

**Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Specifies the scale of the input that an expression set processes. The scale determines where the expression set is executed.

- 

**Possible values**:

  - `High`

  - `Low`

### ExpressionSetDefinitionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The expression set definition record associated with this expression set. This is a required field.

This is a relationship field.

- 

**Relationship Name**: ExpressionSetDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: ExpressionSetDefinition

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record, a record related to this record, or a list view.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, it’s possible the user only accessed this record or list view (LastReferencedDate) but didn’t view it.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the expression set. This is a required field.

### OwnerId

- 

**Type**: reference

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: The ID of the user who currently owns this expression set.

This is a polymorphic relationship field.

- 

**Default value**: the user logged in to the API to perform the create action

- 

**Relationship Name**: Owner

- 

**Relationship Type**: Lookup

- 

**Refers To**: Group, User

### Type

- 

**Type**: picklist

- 

**Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: The type of the expression set.

- 

**Possible values**:

  - `Custom`

  - `Standard`

### UsageType

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: The type of industry that’s using the expression set.

**Note:**

When Business Rules Engine is enabled for a Salesforce instance, the default value is ‘`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets.

- 

**Possible values**:

  - `Bre`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-expressionset.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
