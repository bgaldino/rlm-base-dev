---
page_id: sforce-api-objects-expressionsetdefinitioncontextdefinition
title: ExpressionSetDefinitionContextDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-expressionsetdefinitioncontextdefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-standard-objects
legacy_page_id: sforce_api_objects_expressionsetdefinitioncontextdefinition.htm
fetched_at: 2026-11-25
---

# ExpressionSetDefinitionContextDefinition

Represents a relationship between an expression set definition and a context definition. This object is available in API version 58.0 and later.

**Note:**

You can’t add records to this object.

## Fields

### ContextDefinitionApiName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: API name of the context definition.

### ContextDefinitionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: ID of the context definition.

This field is a relationship field.

- 

**Relationship Name**: ContextDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextDefinition

### ExecutableContextDefinition

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: Developer name of the file-based context definition.

### ExpressionSetApiName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: API name of the expression set.

### ExpressionSetDefinitionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: ID of the expression set definition.

This field is a relationship field.

- 

**Relationship Name**: ExpressionSetDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: ExpressionSetDefinition

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-expressionsetdefinitioncontextdefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
