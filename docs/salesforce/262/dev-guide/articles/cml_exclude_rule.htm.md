---
page_id: cml_exclude_rule.htm
title: Exclude Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_exclude_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Exclude Rule

The exclude rule is used to automatically remove a specific type in a relationship if a
certain condition is met.

The exclude rule has this syntax.

```
exclude(logic expression, relationship[type],"Explanation message");
```

The type must be leaf type, a node without children.

In the exclude rule, if a user sets attribute values in Product Catalog Management (PCM)
that violate the rule requirements, the constraint engine overrides the user input in order
to validate the constraint. This behavior is different than other constraints, in which the
constraint engine doesn't override user input, but displays an error if user input
violates the constraint. See How User Input Order Affects Constraint Engine Behavior section
in [Logical Constraints](./cml_logical_constraints.htm.md "A logical constraint defines a statement that must hold true logically. The constraint can be any logical expression by using a logical operator.").

In this example, the exclude rule automatically removes the `Heater_120` heater from the type `GeneratorSet` if the `Voltage3` is greater
than or equal to `4160`.

```
type GeneratorSet {
int Voltage3 = [120..13800];
relation Heaters : Heater_120 [1..3];
exclude(Voltage3 >= 4160, Heaters[Heater_120]);
}
type Heater_120 {}
```
