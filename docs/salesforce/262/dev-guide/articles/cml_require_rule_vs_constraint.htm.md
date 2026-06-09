---
page_id: cml_require_rule_vs_constraint.htm
title: Require Rule vs Constraint
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule_vs_constraint.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
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
