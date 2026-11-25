---
page_id: cml-best-practice-scale
title: "Decimals and Doubles: Consider the Impact of Scale on Performance"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-scale.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_scale.htm
fetched_at: 2026-11-25
---

# Decimals and Doubles: Consider the Impact of Scale on Performance

Scale is the number of digits that follow the decimal point in a decimal or double. Consider its impact on performance before using decimals and doubles in expressions.

In a decimal or double, scale is the number of digits that follow the decimal point. Using decimals and doubles in expressions can cause performance problems due to the number of permutations.

In this example, myNumber is a double with a scale of 2. The value can be 0.00, 0.01, 0.02, all the way up to 2.99, which can impact constraint engine performance:

```
double(2) myNumber = [0..3];
```

In this example, myNumber is an integer. The value can only be 0, 1, 2 or 3, which has less impact on constraint engine performance:

```
int myNumber = [0..3];
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-scale.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
