---
page_id: cml_require_rule_vs_constraint.htm
title: Require Rule vs Constraint
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule_vs_constraint.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-11-23
---

# Require Rule vs Constraint

In Constraint Modeling Language (CML), constraint() and require() can both enforce
behavior, but they operate differently: constraint focuses on logical consistency, require
focuses on physical presence of products.

Here's a comparison between `constraint()` and
`require()`.

| Feature | constraint() | require() |
| --- | --- | --- |
| Primary goal | Validates if a condition is met (LHS) and operates on the result (RHS). | Forces a product to be present. |
| Engine action | Resolves the constraint or displays an error if there are no options to resolve. | Adds the required product to the quote. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule_vs_constraint.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
