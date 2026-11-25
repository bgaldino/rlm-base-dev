---
page_id: cml-best-practice-cardinality
title: "Relationship Cardinality: Specify the Smallest Range Required"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-cardinality.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_cardinality.htm
fetched_at: 2026-11-25
---

# Relationship Cardinality: Specify the Smallest Range Required

Specify the smallest required cardinality for a variable so the constraint engine tests fewer combinations of values and performs better.

In a relationship, cardinality is the quantity of instances of the same type. Specify the smallest required cardinality for a variable, to avoid testing unneeded combinations of values. If you specify a higher cardinality than required, or don’t specify cardinality, the constraint engine tests more combinations, which impacts performance.

This example doesn’t specify cardinality. The constraint engine tries to set a quantity with 1, 2, 3, all the way up to 9,999:

```
relation engine : Engine;
```

This example specifies minimum and maximum cardinality as 0 and 1, so the constraint engine sets the quantity to 1. The engine tests fewer combinations to find a solution.

```
relation engine : Engine[0..1];
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-cardinality.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
