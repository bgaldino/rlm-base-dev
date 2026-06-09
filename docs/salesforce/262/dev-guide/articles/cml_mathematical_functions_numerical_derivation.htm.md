---
page_id: cml_mathematical_functions_numerical_derivation.htm
title: Mathematical Functions (Numerical Derivation)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_mathematical_functions_numerical_derivation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_variables.htm
fetched_at: 2026-06-09
---

# Mathematical Functions (Numerical Derivation)

Mathematical functions and operators are used to calculate derived values based on
arithmetic relationships between variables.

| Function/Operator | Purpose | CML Keyword/Operator [Source] |
| --- | --- | --- |
| Arithmetic Operators | Perform standard arithmetic: addition (+), subtraction (-), multiplication (\*), division (/), modulo (% or mod), and power (^). | `+, -, *, /, %, ^` |
| ceil() | Returns the smallest integer greater than or equal to the argument (rounds up). | `ceil` |

## Usage Example

```
surgeLoadKW == requiredKW * 1.25);
ceil(totalItems / itemsPerCrate)
```

See [Arithmetic Calculations and Functions](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.") and examples [here](./cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm.md "Constraint Modeling Language (CML) must accurately calculate the total sum or aggregate of specific attributes like quantity or userCount across child components, especially in complex configurations requiring group-level aggregation").
