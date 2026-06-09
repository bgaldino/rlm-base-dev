---
page_id: pricing_tooling_api_parent.htm
title: Salesforce Pricing Tooling API Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pricing_tooling_api_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_overview.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Tooling API Objects

Tooling API exposes metadata used in developer tooling that you can access through REST
or SOAP. Tooling API’s SOQL capabilities for many metadata types allow you to retrieve smaller
pieces of metadata.

- **[PricingActionParameters](./sforce_api_objects_pricingactionparameters.htm.md)**  
  Represents a pricing action associated to a context definition and a pricing procedure. This object is available in API version 60.0 and later.
- **[PricingProcedureOutputMap](./sforce_api_objects_pricingprocedureoutputmap.htm.md)**  
  Represents the mapping of the outputs of the pricing procedures to the associated lookup tables. Each record specifies the output mapping of the associated lookup table based on the pricing component type specified in the Pricing Recipe Table Mapping object. This object is available in API version 60.0 and later.
- **[PricingRecipe](./sforce_api_objects_pricingrecipe.htm.md)**  
  Represents one out of various data models or sets of entities of a particular cloud that'll be consumed by the pricing data store during design and run time. This object is available in API version 60.0 and later.
- **[PricingRecipeTableMapping](./sforce_api_objects_pricingrecipetablemapping.htm.md)**  
  Represents the mapping of pricing components of a lookup table with the chosen pricing recipe. This object is available in API version 60.0 and later.
- **[ProcedureOutputResolution](./sforce_api_objects_procedureoutputresolution.htm.md)**  
  Represents the pricing resolution for an pricing element determined using strategy name and formula. This object is available in API version 63.0 and later.
- **[ProcedurePlanCriterion](./tooling_api_objects_procedureplancriterion.htm.md)**  
  Represents a criterion within a procedure plan option record. This object is available in API version 62.0 and later.
- **[ProcedurePlanDefinition](./tooling_api_objects_procedureplandefinition.htm.md)**  
  Represents the setup of a unified procedure from a list of multiple procedures that can be sequenced in any order based on business needs. Each procedure plan definition contains sections and subsections where procedures can be configured by using a lookup table or rule-based criteria. This object is available in API version 62.0 and later.
- **[ProcedurePlanDefinitionVersion](./tooling_api_objects_procedureplandefinitionversion.htm.md)**  
  Represents the versions for a procedure plan definition. Multiple versions under a procedure plan definition must be active at a time, which can be resolved at run time using the rank field. This object is available in API version 62.0 and later.
- **[ProcedurePlanOption](./tooling_api_objects_procedureplanoption.htm.md)**  
  Represents the selection criteria of how a procedure can be configured for a selected procedure plan section record. This object is available in API version 62.0 and later.
- **[ProcedurePlanSection](./tooling_api_objects_procedureplansection.htm.md)**  
  Represents various procedure setup sections for a procedure plan definition. Each section enables the setup of a procedure of a type that can be further determined by using a rule-based criteria or it can be set based on a selected lookup table. This object is available in API version 62.0 and later.
- **[ProcedurePlanVariable](./tooling_api_objects_procedureplanvariable.htm.md)**  
  Represents the setup for any adhoc user-defined variable that can be linked to a procedure plan definition record. This object is available in API version 62.0 and later.

#### See Also

- [*Tooling API Developer Guide*: Introducing Tooling API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_tooling.meta/api_tooling/intro_api_tooling.htm "Tooling API Developer Guide: Introducing Tooling API - HTML (New Window)")
