---
page_id: expression_set_standard_objects.htm
title: Expression Set Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/expression_set_standard_objects.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_parent.htm
fetched_at: 2026-06-25
---

# Expression Set Standard Objects

Use standard objects to create, update, and activate Expression Set
components.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Professional**, **Unlimited**, and **Developer** Editions |

- **[ExpressionSet](./sforce_api_objects_expressionset.htm.md)**  
  Represents information about an expression set. An expression set performs a series of calculations using lookups and user-defined variables and constants. This object is available in API version 55.0 and later.
- **[ExpressionSetDefinitionContextDefinition](./sforce_api_objects_expressionsetdefinitioncontextdefinition.htm.md)**  
  Represents a relationship between an expression set definition and a context definition. This object is available in API version 58.0 and later.
- **[ExpressionSetVersion](./sforce_api_objects_expressionsetversion.htm.md)**  
  Represents information about a specific version of an expression set. This object is also accessible through the UI API, which enables its use in components like Lightning Web Components (LWC). This object is available in API version 55.0 and later.
- **[ExpressionSetView](./sforce_api_objects_expressionsetview.htm.md)**  
  Represents a virtual object that provides a consolidated view of file-based expression set. File-based expression sets are read-only templates. To be able to modify file-based expression sets, you must clone them first. This object is available in API version 55.0 and later.
- **[ExpsSetObjectAliasFieldVw](./sforce_api_objects_expssetobjectaliasfieldvw.htm.md)**  
  Represents the virtual object that provides a consolidated view of source object and its alias, and the source object fields and their aliases that are used in an expression set. This object is used to check the permission level required to access the underlying object fields associated with their field aliases. This object is available in API version 56.0 and later.
