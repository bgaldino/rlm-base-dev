---
page_id: sforce_api_objects_expressionsetdefinitioncontextdefinition.htm
title: ExpressionSetDefinitionContextDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_expressionsetdefinitioncontextdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_standard_objects.htm
fetched_at: 2026-06-25
---

# ExpressionSetDefinitionContextDefinition

Represents a relationship between an expression set definition and a
context definition. This object is available in API version 58.0 and
later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

You can’t add records to this object.

## Fields

| Field | Details |
| --- | --- |
| ContextDefinitionApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  API name of the context definition. |
| ContextDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the context definition.  This field is a relationship field.  Relationship Name  ContextDefinition  Relationship Type  Lookup  Refers To  ContextDefinition |
| ExecutableContextDefinition | Type  string  Properties  Create, Filter, Group, Nillable, Sort  Description  Developer name of the file-based context definition. |
| ExpressionSetApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  API name of the expression set. |
| ExpressionSetDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the expression set definition.  This field is a relationship field.  Relationship Name  ExpressionSetDefinition  Relationship Type  Lookup  Refers To  ExpressionSetDefinition |
