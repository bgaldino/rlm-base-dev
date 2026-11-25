---
page_id: cml-mathematical-functions-numerical-derivation
title: Mathematical Functions (Numerical Derivation)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-mathematical-functions-numerical-derivation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-variables
legacy_page_id: cml_mathematical_functions_numerical_derivation.htm
fetched_at: 2026-11-25
---

# Mathematical Functions (Numerical Derivation)

Mathematical functions and operators are used to calculate derived values based on arithmetic relationships between variables.

| Function/Operator | Purpose | CML Keyword/Operator [Source] |
| --- | --- | --- |
| Arithmetic Operators | Perform standard arithmetic: addition (+), subtraction (-), multiplication (*), division (/), modulo (% or mod), and power (^). | `+, -, *, /, %, ^` |
| ceil() | Returns the smallest integer greater than or equal to the argument (rounds up). | `ceil` |

## Usage Example

```
surgeLoadKW == requiredKW * 1.25);
ceil(totalItems / itemsPerCrate)
```

See [Arithmetic Calculations and Functions](./cml-core-concept-examples.md) and examples [here](./cml-business-centric-cml-guidelines-quantity-and-aggregation-fun.md).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-mathematical-functions-numerical-derivation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
