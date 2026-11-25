---
page_id: cml-cml-core-concepts
title: Core Concepts
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-cml-core-concepts.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-what-is-constraint-modeling-language
legacy_page_id: cml_cml_core_concepts.htm
fetched_at: 2026-11-25
---

# Core Concepts

Constraint Modeling Language (CML) includes components that cover high-level global configurations to specific data types and constraints.

See these topics for information on each core concept and the ways they work together.

**Note:**

CML supports single-line code comments with // and block comments with /* */.

- 

**[How CML Fits in the Product Configure Business API Pipeline](./cml-configure-business-api-pipeline.md)**

When you call the Product Configure Business API, the request runs through a fixed sequence of stages. The CML constraint engine is one stage in that sequence, and where it runs determines which data it can see.

- 

**[Global Properties and Settings](./cml-global-properties-and-settings.md)**

Header-level declarations define the global properties and settings for a model, including constants, properties, and external values that set up the foundation of the CML code.

- 

**[Variables](./cml-variables.md)**

Variables are the properties or characteristics defined within a type. Variables can hold different types of data and can be calculated from other values.

- 

**[Types](./cml-types.md)**

In Constraint Modeling Language (CML), you define types to represent entities or objects in the model. Types are the foundational building blocks of CML. A type encapsulates the property, relationships, constraint, and rules for the entity.

- 

**[Relationships](./cml-relationships.md)**

Relationships in Constraint Modeling Language (CML) define how different product types are associated with each other, forming the structural hierarchy of a product bundle. Relationships are also referred to as ports.

- 

**[Constraints](./cml-constraints.md)**

Constraints enforce rules and conditions on types, variables, and relationships. Use constraints to define logical restrictions and ensure consistency within the model.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-cml-core-concepts.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
