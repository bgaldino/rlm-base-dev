---
page_id: cml-cml-best-practices
title: Constraint Modeling Language (CML) Best Practices
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-cml-best-practices.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-what-is-constraint-modeling-language
legacy_page_id: cml_cml_best_practices.htm
fetched_at: 2026-11-25
---

# Constraint Modeling Language (CML) Best Practices

To prevent performance degradation or unexpected behaviors when the constraint engine executes CML code, follow these practices when writing code.

For performance guidelines and tips on troubleshooting, see [Debugging Constraint Modeling Language (CML)](./cml-debugging-cml.md).

- 

**[Relationship Cardinality: Specify the Smallest Range Required](./cml-best-practice-cardinality.md)**

Specify the smallest required cardinality for a variable so the constraint engine tests fewer combinations of values and performs better.

- 

**[Decimals and Doubles: Consider the Impact of Scale on Performance](./cml-best-practice-scale.md)**

Scale is the number of digits that follow the decimal point in a decimal or double. Consider its impact on performance before using decimals and doubles in expressions.

- 

**[Variable Domains: Keep Domains as Small as Possible](./cml-best-practice-domains.md)**

A variable domain is the set of all possible values that the variable can take. Keep domains as small as possible to reduce the combinations that the constraint engine tests.

- 

**[Calculating Values: Put Calculations Inside of Constraints](./cml-best-practice-calculations.md)**

To calculate a value, put the calculation inside of a constraint instead of in an inline expression.

- 

**[Relationships: Combine Relationships to Reduce Performance Impact](./cml-best-practice-combine-relationships.md)**

Creating multiple relationships on a type can impact performance. When possible, combine relationships to improve performance.

- 

**[Sequence: Use the Sequence Variable Annotation to Specify the Order of Execution](./cml-best-practice-sequence.md)**

Use the sequence variable annotation to specify the order in which the constraint engine sets values for a constraint model’s attributes and relationships.

- 

**[Sequence and Configurable](./cml-best-practice-sequence-configurable.md)**

Using the configurable property with the sequence variable affects how the solver handles attributes and whether it overrides user input.

- 

**[Automatically Add a Product: Define as a Separate Constraint](./cml-best-practice-add-product.md)**

To automatically add a product and also set attributes on the product, define these procedures as separate constraints.

- 

**[Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes](./cml-best-practice-attribute-name.md)**

When a constraint model is active, include the attribute developer name in Product Configurator API requests that create or update a product attribute.

- 

**[Access Quantity in CML: Cardinality and Attribute Constraints](./cml-best-practice-access-quantity.md)**

There are two ways to access quantity in CML. Use cardinality constraints and attribute constraints correctly for best performance.

- 

**[Pricing Fields Not Supported in CML](./cml-best-practice-pricing-fields.md)**

Pricing fields, such as ListPrice and NetUnitPrice, aren’t supported in CML and shouldn’t be used in constraint models.

- 

**[Configure Child or Grandchild Products Based on Parent Product](./cml-best-practice-parent-products.md)**

Use the parent keyword to configure child and grandchild products dynamically based on the parent product.

- 

**[PCG Group Relations: Follow Order in Constraints](./cml-best-practice-pcg-group-relations.md)**

Order the Product Component Group (PCG) group relations in the way they appear in the constraints.

- 

**[Relations Without PCG: Follow Order in Constraints](./cml-best-practice-relation-order.md)**

Order of relations matters for constraint evaluation. Specify the relations used in the left side of the constraints first.

- 

**[Relation Aggregates: Stabilize Preferences Using Staged Variables](./cml-best-practice-relation-aggregates.md)**

To improve solver stability and prevent backtracking, stage relation aggregates through local variables and state anchors instead of referencing them directly in preferences.

- 

**[Virtual Quote Root: Model Cross-Bundle Logic Using a Shared Transaction Parent](./cml-best-practice-virtual-quote-root.md)**

For transaction-level rules that span products that have no parent-child relationship, use a virtual quote as a transaction root pattern.

- 

**[Dependent Logic: Use Configurable Variable Annotation to Prevent Premature Default Assignment](./cml-best-practice-dependent-logic.md)**

Use the configurable variable annotation on a target attribute to prevent the engine from assigning a default value before your calculation and preference rules execute.

- 

**[Consolidate Multiple Default Configurations](./cml-best-practice-consolidate-defaults.md)**

Apply dynamic, overridable default quantities to a single component based on multiple states of a driving attribute, using one derived variable and a single setdefault rule.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-cml-best-practices.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
