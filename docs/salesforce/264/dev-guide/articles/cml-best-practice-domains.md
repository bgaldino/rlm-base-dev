---
page_id: cml-best-practice-domains
title: "Variable Domains: Keep Domains as Small as Possible"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-domains.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_domains.htm
fetched_at: 2026-11-25
---

# Variable Domains: Keep Domains as Small as Possible

A variable domain is the set of all possible values that the variable can take. Keep domains as small as possible to reduce the combinations that the constraint engine tests.

A variable domain is the set of all possible values that the variable can take. In this example, the variable color has a domain with three values:

```
string color = ["Red", "Yellow", "Green"];
```

The larger the domain, the more possible values for the variable, which means more combinations for the engine to test. A large domain can impact performance and lead to slower searches, errors, or unexpected behaviors.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-domains.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
