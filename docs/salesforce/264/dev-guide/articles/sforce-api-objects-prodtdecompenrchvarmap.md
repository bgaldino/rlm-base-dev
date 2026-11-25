---
page_id: sforce-api-objects-prodtdecompenrchvarmap
title: ProdtDecompEnrchVarMap
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-prodtdecompenrchvarmap.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_prodtdecompenrchvarmap.htm
fetched_at: 2026-11-25
---

# ProdtDecompEnrchVarMap

Represents the mapping of a field context tag or an attribute to a variable within an expression set. This object is available in API version 64.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`,

## Fields

### AttributeDefinitionId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The attribute definition the expression set variable is mapped to when creating the enrichment rule.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition

- **Refers To**: AttributeDefinition

### ExpressionSetVarName

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The name of the variable that’s mapped to the expression set defined in the enrichment rule.

### FieldContextTagName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The name of the field context tag to which the expression set variable is mapped when creating the enrichment rule.

### ProductAttributeIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The product attribute from an internal or external catalog, used by DRO to copy data during the enrichment process. This field is available in API version 65.0 and later.

### ProductDecompEnrichmentRuleId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: The rule that contains the mappings between the fields and attributes for the decomposing product.

This field is a relationship field.

- **Relationship Name**: ProductDecompEnrichmentRule

- **Relationship Type**: Master-detail

- **Refers To**: ProductDecompEnrichmentRule (the master object)

### VariableType

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Restricted picklist, Sort

- **Description**: Specifies whether the expression set variable is an input or output variable.

Valid values are `Input` or `Output`.

The default value is `Input`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-prodtdecompenrchvarmap.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
