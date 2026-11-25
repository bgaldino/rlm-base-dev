---
page_id: cml-preference-rule
title: Preference Rule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-preference-rule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-constraints
legacy_page_id: cml_preference_rule.htm
fetched_at: 2026-11-25
---

# Preference Rule

The preference rule encourages the constraint solver to satisfy the condition, but doesn’t enforce it if the condition can’t be met.

The system tries to satisfy the condition in a preference rule, but if for some reason it can’t, the system delivers a failure message to the user with `Info` severity.

**Note:**

If a preference rule auto-adds a product that has one or more Product Selling Model Options (PSMOs), set one PSMO on the product to Default. The system uses the default PSMO to determine which pricebook entry to use for the auto-added product. For more information, see [Manage Product Selling Model](https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_selling_model.htm) in Revenue Cloud in Salesforce Help.

The preference rule has this syntax.

```
preference(logic expression, string literal | string variable, argument, .., argument);
preference(logic expression, string literal | string variable);
preference(logic expression);
```

A preference rule can include an optional explanation message for failure. The message is of `Info` severity, meaning it does not block the user from continuing with the action.

In this example, the preference rule encourages the user to mention the `dBMax` value as `90` and the `requiredKW` value as `500`.

```
type GeneratorSet {
   int requiredKW = [101..10000];
   int dBMax = [0..140];
   preference(dBMax == 90, "90 preferred for dbMax");
   preference(requiredKW == 500,"50 preferred for requiredKW");
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-preference-rule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
