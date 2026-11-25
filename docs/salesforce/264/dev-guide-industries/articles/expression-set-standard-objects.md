---
page_id: expression-set-standard-objects
title: Expression Set Standard Objects
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/expression-set-standard-objects.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-parent
legacy_page_id: expression_set_standard_objects.htm
fetched_at: 2026-11-25
---

# Expression Set Standard Objects

Use standard objects to create, update, and activate Expression Set components.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Professional**, **Unlimited**, and **Developer** Editions |

- 

**[ExpressionSet](./sforce-api-objects-expressionset.md)**

Represents information about an expression set. An expression set performs a series of calculations using lookups and user-defined variables and constants. This object is available in API version 55.0 and later.

- 

**[ExpressionSetDefinitionContextDefinition](./sforce-api-objects-expressionsetdefinitioncontextdefinition.md)**

Represents a relationship between an expression set definition and a context definition. This object is available in API version 58.0 and later.

- 

**[ExpressionSetVersion](./sforce-api-objects-expressionsetversion.md)**

Represents information about a specific version of an expression set. This object is also accessible through the UI API, which enables its use in components like Lightning Web Components (LWC). This object is available in API version 55.0 and later.

- 

**[ExpressionSetView](./sforce-api-objects-expressionsetview.md)**

Represents a virtual object that provides a consolidated view of file-based expression set. File-based expression sets are read-only templates. To be able to modify file-based expression sets, you must clone them first. This object is available in API version 55.0 and later.

- 

**[ExpsSetObjectAliasFieldVw](./sforce-api-objects-expssetobjectaliasfieldvw.md)**

Represents the virtual object that provides a consolidated view of source object and its alias, and the source object fields and their aliases that are used in an expression set. This object is used to check the permission level required to access the underlying object fields associated with their field aliases. This object is available in API version 56.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/expression-set-standard-objects.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
