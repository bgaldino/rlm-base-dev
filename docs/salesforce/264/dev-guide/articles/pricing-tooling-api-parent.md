---
page_id: pricing-tooling-api-parent
title: Salesforce Pricing Tooling API Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-tooling-api-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-overview
legacy_page_id: pricing_tooling_api_parent.htm
fetched_at: 2026-11-25
---

# Salesforce Pricing Tooling API Objects

Tooling API exposes metadata used in developer tooling that you can access through REST or SOAP. Tooling API’s SOQL capabilities for many metadata types allow you to retrieve smaller pieces of metadata.

- 

**[PricingActionParameters](./sforce-api-objects-pricingactionparameters.md)**

Represents a pricing action associated to a context definition and a pricing procedure. This object is available in API version 60.0 and later.

- 

**[PricingProcedureOutputMap](./sforce-api-objects-pricingprocedureoutputmap.md)**

Represents the mapping of the outputs of the pricing procedures to the associated lookup tables. Each record specifies the output mapping of the associated lookup table based on the pricing component type specified in the Pricing Recipe Table Mapping object. This object is available in API version 60.0 and later.

- 

**[PricingRecipe](./sforce-api-objects-pricingrecipe.md)**

Represents one out of various data models or sets of entities of a particular cloud that’ll be consumed by the pricing data store during design and run time. This object is available in API version 60.0 and later.

- 

**[PricingRecipeTableMapping](./sforce-api-objects-pricingrecipetablemapping.md)**

Represents the mapping of pricing components of a lookup table with the chosen pricing recipe. This object is available in API version 60.0 and later.

- 

**[ProcedureOutputResolution](./sforce-api-objects-procedureoutputresolution.md)**

Represents the pricing resolution for an pricing element determined using strategy name and formula. This object is available in API version 63.0 and later.

- 

**[ProcedurePlanCriterion](./tooling-api-objects-procedureplancriterion.md)**

Represents a criterion within a procedure plan option record. This object is available in API version 62.0 and later.

- 

**[ProcedurePlanDefinition](./tooling-api-objects-procedureplandefinition.md)**

Represents the setup of a unified procedure from a list of multiple procedures that can be sequenced in any order based on business needs. Each procedure plan definition contains sections and subsections where procedures can be configured by using a lookup table or rule-based criteria. This object is available in API version 62.0 and later.

- 

**[ProcedurePlanDefinitionVersion](./tooling-api-objects-procedureplandefinitionversion.md)**

Represents the versions for a procedure plan definition. Multiple versions under a procedure plan definition must be active at a time, which can be resolved at run time using the rank field. This object is available in API version 62.0 and later.

- 

**[ProcedurePlanOption](./tooling-api-objects-procedureplanoption.md)**

Represents the selection criteria of how a procedure can be configured for a selected procedure plan section record. This object is available in API version 62.0 and later.

- 

**[ProcedurePlanSection](./tooling-api-objects-procedureplansection.md)**

Represents various procedure setup sections for a procedure plan definition. Each section enables the setup of a procedure of a type that can be further determined by using a rule-based criteria or it can be set based on a selected lookup table. This object is available in API version 62.0 and later.

- 

**[ProcedurePlanVariable](./tooling-api-objects-procedureplanvariable.md)**

Represents the setup for any adhoc user-defined variable that can be linked to a procedure plan definition record. This object is available in API version 62.0 and later.

**See Also**

- [*Tooling API Developer Guide*: Introducing Tooling API](https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/intro_api_tooling.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/pricing-tooling-api-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
