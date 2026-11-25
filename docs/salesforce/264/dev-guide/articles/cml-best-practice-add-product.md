---
page_id: cml-best-practice-add-product
title: "Automatically Add a Product: Define as a Separate Constraint"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-add-product.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_add_product.htm
fetched_at: 2026-11-25
---

# Automatically Add a Product: Define as a Separate Constraint

To automatically add a product and also set attributes on the product, define these procedures as separate constraints.

If you need to automatically add a product, and also set attributes on the product, define these procedures as separate constraints, as in this example.

```
constraint(laptop[Laptop] > 0, warranty[Warranty] > 0);
constraint(warranty[Warranty] > 0, warranty[Warranty].type == “Premium”);
```

Avoid this example, which automatically adds a product and sets attributes on the product, in the same constraint.

```
constraint(laptop[Laptop] > 0, warranty[Warranty] > 0 && warranty[Warranty].type == "Premium");
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-add-product.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
