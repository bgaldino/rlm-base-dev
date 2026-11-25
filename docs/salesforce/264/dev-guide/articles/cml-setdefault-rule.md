---
page_id: cml-setdefault-rule
title: Setdefault Rule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-setdefault-rule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-constraints
legacy_page_id: cml_setdefault_rule.htm
fetched_at: 2026-11-25
---

# Setdefault Rule

The setdefault rule allows component selection with attribute values and quantity, similar to the require rule.

Unlike the require rule, the setdefault rule applies a default configuration status and uses a triggering mechanism to control when the solver attempts to satisfy the rule. The setdefault rule can include an optional explanation message.

The setdefault has this syntax, similar to the require rule.

```
setdefault(condition, expression, message);
```

The setdefault rule evaluates the condition.

- 

If the condition was never true or is false on initial evaluation, the solver doesn’t attempt to satisfy the expression and doesn’t show a message, regardless of whether any part of the condition is changed

- 

If the condition was previously true and changes to false, the solver reverts any configuration state changes, such as product selections or quantity adjustments, that were applied when the condition was true. The configuration returns to the state it would be in without the setdefault rule.

- 

If the condition is true, the solver performs one of these actions.

  - If any part of the condition is changed or the parent component is new, the solver attempts to satisfy the expression. If the solver can’t satisfy the expression, an explanation message is shown (if included).

  - If no part of the condition is changed, the solver evaluates the expression without attempting to satisfy it. If the expression evaluates to false, an explanation message is shown (if included).

The key difference between the setdefault rule and the require rule is that the setdefault rule attempts to satisfy the expression only when a condition is changed. If no condition is changed, the setdefault rule performs a passive evaluation. The require rule always attempts to satisfy the expression when the condition is true.

In this scenario, we use the requiredKW attribute (the user’s power requirement) as the condition and the Accessories relation as the target for the recommended cardinality.

```
type Accessory;
type GeneratorSet  {
int requiredKW = [101..10000];
relation Accessories : Accessory[1..99];
/**
* @Title High Power Accessory Recommendation
* The setdefault constraint specifies that 2 accessory units are
* recommended when the required power capacity is greater than 2000 kW.
*/
setdefault(
requiredKW > 2000,
Accessories[Accessory] == 2,
"2 specialized accessory kits are recommended for power levels above 2000 kW"
);
}
```

The setdefault rule doesn’t revert values when the triggering condition becomes false. After the solver sets a value, that value persists even if the condition is no longer met. If you need a value to revert, use the constraint rule instead. Note that the constraint rule removes the user’s ability to override the value.

In this scenario, the user expects the accessory quantity to reset to 0 when the required power capacity drops to 2000 kW or below. Because setdefault doesn’t revert values, the quantity stays at 2.

```
type Accessory;
type GeneratorSet  {
int requiredKW = [101..10000];
relation Accessories : Accessory[0..99];
/**
* @Title High Power Accessory Recommendation
* The setdefault constraint recommends 2 accessory units when the
* required power capacity is greater than 2000 kW.
*/
setdefault(
requiredKW > 2000,
Accessories[Accessory] == 2,
"2 specialized accessory kits are recommended for power levels above 2000 kW"
);
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-setdefault-rule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
