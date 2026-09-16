---
page_id: cml_exclude_rule.htm
title: Exclude Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_exclude_rule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Exclude Rule

The exclude rule automatically removes a specific type in a relationship if a certain
    condition is true.

    
      

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
        in [Logical Constraints](./cml_logical_constraints.htm.md).

      

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

    

    

## Exclude a Child Product Based on Another Child
        Product's Attribute

When a bundle contains multiple child products, you can
        exclude one child product based on an attribute value set on a sibling child product. To
        evaluate a child product's attributes from the parent scope, use the `count()` aggregate function on the parent's relation. The
          `count()` function inspects instances within a relation
        and counts those that match a given condition. When the count is greater than zero, at least
        one child instance satisfies the condition, and the exclude rule acts on that
        result.

Use this
        pattern.

```
exclude(<relation>.count(<ChildType>.<attribute> == <value>) > 0, <otherRelation>[<OtherChildType>], "Explanation message");
```

In
        this example, the `GeneratorSet` bundle contains both
          `Heater` and `StandardCooler` child products. If any `Heater` in the configuration has an `outputClass` of `High-Output`, the `StandardCooler` is automatically excluded because high-output
        heaters require an industrial-grade
      cooler.

```
type Heater {
string outputClass = ["Standard-Output", "High-Output"];
}
type StandardCooler {}
type GeneratorSet {
relation Heaters : Heater[0..10];
relation Coolers : StandardCooler[0..5];
exclude(Heaters.count(Heater.outputClass == "High-Output") > 0, Coolers[StandardCooler],
  "High-output heaters require an industrial cooler, not a standard cooler.");
}

```
