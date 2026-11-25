---
page_id: cml-constraint-model-example-modeling-a-generator-set
title: Modeling a Generator Set
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-constraint-model-example-modeling-a-generator-set.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-what-is-constraint-modeling-language
legacy_page_id: cml_constraint_model_example_modeling_a_generator_set.htm
fetched_at: 2026-11-25
---

# Modeling a Generator Set

The Constraint Model for a Generator Set examples use CML to define a technical power configuration, illustrating concepts such as calculated variables, enforcement of external standards, and component selection based on requirements.

The [examples](./cml-core-concept-examples.md) correspond to the [CML core concepts](./cml-cml-core-concepts.md) linked here. See the Generator Set examples for code samples that use the core concepts.

- Global Properties and Settings—`VOLTAGE_REGEX` is a global constant that defines a fixed regular expression pattern used for validation or parsing throughout the model.

- Types—`GeneratorSet` is the root type that represents the main entity. `GeneralModel` represents a related component type.

- Variables—The `GeneratorSet` type defines variables like `requiredKW` (the user’s power requirement), `Voltage`, and calculated variables like `surgeLoadKW` and `Voltage3` (derived from parsing the `Voltage` string).

- Relationships—The `GeneralModels` relation connects the `GeneratorSet` type to its possible configurations (`GeneralModel`).

- Constraints—Constraints enforce critical business rules and safety standards, such as ensuring the selected generator model’s power meets the required threshold, or restricting configuration options (such as `Voltage`) based on the specified compliance standards (`Listing-UL 2200`).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-constraint-model-example-modeling-a-generator-set.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
