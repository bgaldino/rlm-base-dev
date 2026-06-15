---
page_id: sforce_api_objects_productdecompenrichmentrule.htm
title: ProductDecompEnrichmentRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productdecompenrichmentrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductDecompEnrichmentRule

Represents mappings between fields and attributes. Enrichment rules are part
of a decomposition rule, and are used to propagate data to fulfillment order lines.
This object is available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| CalculationDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  An expression set or a decision matrix that calculates the destination value.  This field is a polymorphic relationship field.  Relationship Name  CalculationDefinition  Refers To  DecisionMatrixDefinition, ExpressionSet |
| CalculationMethod | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of enrichment rule.  Valid values are:  - `Ad-verbatim`—As   Is - `Static-Lookup`—List Lookup - `Expression-Set`—Available in API version 64.0   and later |
| DecompositionRuleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The identifier of the decomposition rule.  This field is a relationship field.  Relationship Name  DecompositionRule  Relationship Type  Parent-child  Refers To  ProductFulfillmentDecompRule (the master object) |
| DestinationApiName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The API name of the destination field or attribute code of an attribute. |
| DestinationAttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  DestinationAttributeDefinition  Refers To  AttributeDefinition |
| DestinationAttributeIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The destination entity attribute that is mapped from the source entity attribute. This field can store a Salesforce AttributeDefinition ID or an external identifier. This field is available in API version 65.0 and later. |
| DestinationContextTag | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the destination context definition. |
| DestinationType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The destination type for mapping.  Valid values are:  - `Attribute` - `Field` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date when a user viewed this record |
| ListMappingGroupId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  ListMappingGroup  Refers To  ValTfrmGrp |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the decomposition rule. |
| RuleEnforcement | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether the rule applies to all fulfillment requests or only to specific ones.  Valid values are:  - `AllFulfillmentRequests` - `InitialFulfillmentRequest`  This field is available in API version 63.0 and later. |
| SourceApiName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The API name of the source field or attribute code of an attribute. |
| SourceAttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  For internal use only.  This field is a relationship field.  Relationship Name  SourceAttributeDefinition  Refers To  AttributeDefinition |
| SourceAttributeIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The source entity attribute that is mapped to the destination entity attribute. This field can store a Salesforce AttributeDefinition ID or an external identifier. This field is available in API version 65.0 and later. |
| SourceContextTag | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The source type for the context definition. |
| SourceType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The source type for mapping.  Valid values are:  - `Attribute` - `Field` |
