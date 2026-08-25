---
page_id: cml_constraint_model_example_modeling_a_generator_set.htm
title: Modeling a Generator Set
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_constraint_model_example_modeling_a_generator_set.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Modeling a Generator Set

The Constraint Model for a Generator Set examples use CML to define a technical power
    configuration, illustrating concepts such as calculated variables, enforcement of external
    standards, and component selection based on requirements.

    

The [examples](./cml_core_concept_examples.htm.md) correspond to the [CML core concepts](./cml_cml_core_concepts.htm.md) linked here. See the Generator Set
      examples for code samples that use the core concepts.

    

- Global Properties and Settings—`VOLTAGE_REGEX` is a
        global constant that defines a fixed regular expression pattern used for validation or
        parsing throughout the model.

      
- Types—`GeneratorSet` is the root type that
        represents the main entity. `GeneralModel` represents a
        related component type.

      
- Variables—The `GeneratorSet` type defines
        variables like `requiredKW` (the user's power
        requirement), `Voltage`, and calculated variables like
          `surgeLoadKW` and `Voltage3` (derived from parsing the `Voltage`
        string).

      
- Relationships—The `GeneralModels` relation
        connects the `GeneratorSet` type to its possible
        configurations (`GeneralModel`).

      
- Constraints—Constraints enforce critical business rules and safety standards, such
        as ensuring the selected generator model's power meets the required threshold, or
        restricting configuration options (such as `Voltage`)
        based on the specified compliance standards (`Listing-UL
          2200`).
