---
page_id: cml_best_practice_combine_relationships.htm
title: "Relationships: Combine Relationships to Reduce Performance Impact"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_combine_relationships.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-11-23
---

# Relationships: Combine Relationships to Reduce Performance Impact

Creating multiple relationships on a type can impact performance. When possible, combine
relationships to improve performance.

Creating multiple relationships on a type can impact performance. When possible, combine
relationships to improve performance.

When possible, avoid this example, which includes separate relationships for Mouse and
Keyboard, two accessories in a product bundle:

```
relation mouse : Mouse;
relation keyboard : Keyboard;
```

Follow this example, which uses one relationship for Accessories, which can include Mouse,
Keyboard, and other accessories.

```
relation accessories : Accessories;
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_combine_relationships.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
