---
page_id: cml_best_practice_sequence_configurable.htm
title: Sequence and Configurable
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_sequence_configurable.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Sequence and Configurable

Using the configurable property with the sequence variable affects how the solver
    handles attributes and whether it overrides user input.

    

Using the `configurable` property with the `sequence` variable affects how the solver handles attributes.
      When configurable is set to `true`, the user can set
      attribute values, and the solver doesn't override user input unless no other solution
      exists. When `configurable` is set to `false`, the solver sets attribute values.

    

In this example for type A, `attribute1` is set to
        `configurable = true`. The user can set the value, and
      the solver doesn't override the user input unless no other solution exists. When the
      left-hand side of the rule is true, the constraint doesn't change `attribute1` to "`Enum3`".

    

```
type A : System {
    @(defaultValue = "Enum1", domainComputation = "true", configurable = true, sequence = 48)
    string attribute1 = ["Enum1", "Enum2", "Enum3"];

  @(configurable = false, defaultValue = "0", sequence = 30)
    decimal(2) attribute2 = f(x, y, z);
    constraint((attribute2 > 3 && attribute2 <= 5) -> attribute1 == "Enum3", "message");
}
```

    

In this example for type B, `attribute1` is set to
        `configurable = false`. The solver propagates values to
      satisfy constraints. When the left-hand side of the rule is true, the constraint
      automatically sets `attribute1` to "`Enum3`".

    

```
type B : System {
    @(defaultValue = "Enum1", domainComputation = "true", configurable = false, sequence = 48)
    string attribute1 = ["Enum1", "Enum2", "Enum3"];

  @(configurable = false, defaultValue = "0", sequence = 30)
    decimal(2) attribute2 = f(x, y, z);
    constraint((attribute2 > 3 && attribute2 <= 5) -> attribute1 == "Enum3", "message");
```

    

Use mindful sequencing in CML to avoid backtracking by the solver when looking for a
      solution, as in this example.

    

```
type LaptopProBundle {

    //relation mouse : Mouse[1..20];
    //The relation mouse has the highest sequence
    relation warranty : Warranty[0..10];
    relation software : Software;
    relation printerBundle : PrinterBundle;
    relation laptop : Laptop[1..10];
    relation mouse : Mouse[1..20];
    //Put highest sequence last to avoid backtracking

    int mouseQty = laptop[Laptop] + warranty[Warranty];

    constraint(mouse[Mouse] > 0 -> mouse[Mouse] == mouseQty,
               "mouse[Mouse] = laptop[Laptop] + warranty[Warranty]");
```
