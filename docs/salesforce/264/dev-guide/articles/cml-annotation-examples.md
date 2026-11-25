---
page_id: cml-annotation-examples
title: Annotation Examples
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-annotation-examples.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-what-is-constraint-modeling-language
legacy_page_id: cml_annotation_examples.htm
fetched_at: 2026-11-25
---

# Annotation Examples

Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model.

The examples explain what each annotation does, where it can be used in the model, what kinds of values it supports, and how it behaves when the configurator runs and evaluates constraints. CML code samples show how the annotation works in practice.

- 

**[closeRelation Annotation](./cml-annotation-example-closerelation.md)**

closeRelation is a CML annotation that controls addition of new line items to the relationship by the engine.

- 

**[configurable Annotation](./cml-annotation-example-configurable.md)**

`configurable` is a CML annotation that controls whether a model element can be configured.

- 

**[defaultValue Annotation](./cml-annotation-example-defaultvalue.md)**

The `defaultValue` annotation is used on a variable to define the value it should start with when configuration begins.

- 

**[domainComputation Annotation](./cml-annotation-example-domaincomputation.md)**

`domainComputation` is a CML annotation that specifies how the domain of a model element is determined, either by using a fixed domain or by computing the domain dynamically during configuration.

- 

**[guardrails Annotation](./cml-annotation-example-guardrails.md)**

guardrails is a CML annotation that prevent the constraint engine from changing specified attributes or relations when it resolves the constraint.

- 

**[peelable Annotation](./cml-annotation-example-peelable.md)**

The `peelable` annotation is used to create soft selection values and allow the engine to modify these selections to satisfy a constraint.

- 

**[productField Annotation](./cml-annotation-example-productfield.md)**

productField is a CML annotation that defines the Product2 field on a variable. productField loads the value from Product Catalog Management (PCM) during constraint model activation.

- 

**[propagateUp Annotation](./cml-annotation-example-propagateup.md)**

`propagateUp` is a Constraint Modeling Language (CML) annotation that controls aggregation propagation between children and parent elements.

- 

**[relatedAttributes Annotation](./cml-annotation-example-relatedattributes.md)**

`relatedAttributes` is a Constraint Modeling Language (CML) annotation that resets the domain to the original one for domainComputation.

- 

**[sequence Annotation](./cml-annotation-example-sequence.md)**

The `sequence` annotation defines the execution and configuration order of elements in a Constraint Modeling Language (CML) model.

- 

**[split Annotation](./cml-annotation-example-split.md)**

`split` is a Constraint Modeling Language (CML) annotation that specifies whether the instances of the type should be split or not.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-annotation-examples.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
