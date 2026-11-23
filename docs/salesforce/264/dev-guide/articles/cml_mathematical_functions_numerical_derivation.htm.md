---
page_id: cml_mathematical_functions_numerical_derivation.htm
title: Mathematical Functions (Numerical Derivation)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_mathematical_functions_numerical_derivation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_variables.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_mathematical_functions_numerical_derivation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
