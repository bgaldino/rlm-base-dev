---
page_id: sforce_api_objects_prodtdecompenrchvarmap.htm
title: ProdtDecompEnrchVarMap
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_prodtdecompenrchvarmap.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProdtDecompEnrchVarMap

Represents the mapping of a field context tag or an attribute to a variable
within an expression set. This object is available in API version 64.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`,

## Fields

| Field | Details |
| --- | --- |
| AttributeDefinitionId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The attribute definition the expression set variable is mapped to when creating the enrichment rule.  This field is a relationship field.  Relationship Name  AttributeDefinition  Refers To  AttributeDefinition |
| ExpressionSetVarName | Type  string  Properties  Filter, Group, Sort  Description  The name of the variable that's mapped to the expression set defined in the enrichment rule. |
| FieldContextTagName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the field context tag to which the expression set variable is mapped when creating the enrichment rule. |
| ProductAttributeIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The product attribute from an internal or external catalog, used by DRO to copy data during the enrichment process. This field is available in API version 65.0 and later. |
| ProductDecompEnrichmentRuleId | Type  reference  Properties  Filter, Group, Sort  Description  The rule that contains the mappings between the fields and attributes for the decomposing product.  This field is a relationship field.  Relationship Name  ProductDecompEnrichmentRule  Relationship Type  Master-detail  Refers To  ProductDecompEnrichmentRule (the master object) |
| VariableType | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Specifies whether the expression set variable is an input or output variable.  Valid values are:  - `Input` - `Output`  The default value is `Input`. |
