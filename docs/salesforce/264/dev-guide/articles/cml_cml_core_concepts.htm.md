---
page_id: cml_cml_core_concepts.htm
title: Core Concepts
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_cml_core_concepts.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Core Concepts

Constraint Modeling Language (CML) includes components that cover high-level global
        configurations to specific data types and constraints.

    
    

See these topics for information on each core concept and the ways they work together.

    

#### Note

CML supports single-line code comments with // and block comments with /*
        */.

            
    

  

- 
**[Global Properties and Settings](./cml_global_properties_and_settings.htm.md)**  

Header-level declarations define the global properties and settings for a model, including     constants, properties, and external values that set up the foundation of the CML code.

- 
**[Variables](./cml_variables.htm.md)**  

Variables are the properties or characteristics defined within a type. Variables can hold     different types of data and can be calculated from other values.

- 
**[Types](./cml_types.htm.md)**  

In Constraint Modeling Language (CML), you define types to represent entities or     objects in the model. Types are the foundational building blocks of CML. A type encapsulates the     property, relationships, constraint, and rules for the entity.

- 
**[Relationships](./cml_relationships.htm.md)**  

Relationships in Constraint Modeling Language (CML) define how different product types     are associated with each other, forming the structural hierarchy of a product bundle.     Relationships are also referred to as ports.

- 
**[Constraints](./cml_constraints.htm.md)**  

Constraints enforce rules and conditions on types, variables, and relationships. Use     constraints to define logical restrictions and ensure consistency within the     model.
