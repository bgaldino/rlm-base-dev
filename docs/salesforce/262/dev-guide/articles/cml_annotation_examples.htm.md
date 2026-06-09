---
page_id: cml_annotation_examples.htm
title: Annotation Examples
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_examples.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-06-09
---

# Annotation Examples

Constraint Modeling Language (CML) annotations are labels that you add to parts of a
model, such as types, variables, relationships, and constraints. Annotations control how these
elements are shown and how they behave in the configurator. Annotations help fine-tune the
configurator and the constraint engine without changing the actual structure of the
model.

The examples explain what each annotation does, where it can be used in the model, what
kinds of values it supports, and how it behaves when the configurator runs and evaluates
constraints. CML code samples show how the annotation works in practice.

- **[closeRelation Annotation](./cml_annotation_example_closeRelation.htm.md)**  
  closeRelation is a CML annotation that controls addition of new line items to the relationship by the engine.
- **[configurable Annotation](./cml_annotation_example_configurable.htm.md)**  
  `configurable` is a CML annotation that controls whether a model element can be configured.
- **[defaultValue Annotation](./cml_annotation_example_defaultValue.htm.md)**  
  The `defaultValue` annotation is used on a variable to define the value it should start with when configuration begins.
- **[domainComputation Annotation](./cml_annotation_example_domainComputation.htm.md)**  
  `domainComputation` is a CML annotation that specifies how the domain of a model element is determined, either by using a fixed domain or by computing the domain dynamically during configuration.
- **[peelable Annotation](./cml_annotation_example_peelable.htm.md)**  
  The `peelable` annotation is used to create soft selection values and allow the engine to modify these selections to satisfy a constraint.
- **[productField Annotation](./cml_annotation_example_productField.htm.md)**  
  productField is a CML annotation that defines the Product2 field on a variable. productField loads the value from Product Catalog Management (PCM) during constraint model activation.
- **[propagateUp Annotation](./cml_annotation_example_propagateUp.htm.md)**  
  `propagateUp` is a Constraint Modeling Language (CML) annotation that controls aggregation propagation between children and parent elements.
- **[relatedAttributes Annotation](./cml_annotation_example_relatedAttributes.htm.md)**  
  `relatedAttributes` is a Constraint Modeling Language (CML) annotation that resets the domain to the original one for domainComputation.
- **[sequence Annotation](./cml_annotation_example_sequence.htm.md)**  
  The `sequence` annotation defines the execution and configuration order of elements in a Constraint Modeling Language (CML) model.
- **[split Annotation](./cml_annotation_example_split.htm.md)**  
  `split` is a Constraint Modeling Language (CML) annotation that specifies whether the instances of the type should be split or not.
