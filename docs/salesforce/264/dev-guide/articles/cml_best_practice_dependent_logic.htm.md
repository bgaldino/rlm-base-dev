---
page_id: cml_best_practice_dependent_logic.htm
title: "Dependent Logic: Use Configurable Variable Annotation to Prevent Premature Default Assignment"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_dependent_logic.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Dependent Logic: Use Configurable Variable Annotation to Prevent Premature Default
    Assignment

Use the configurable variable annotation on a target attribute to prevent the engine
    from assigning a default value before your calculation and preference rules execute.

    

To ensure preference rules correctly set target attributes based on calculated values, use
      the `@(configurable=false)` annotation on the target
      attribute. This prevents a race condition where the engine assigns a default value during
      initialization before your calculation and preference rules execute.

    

When an inline expression is used, CML evaluates the model top-down. If the target attribute
      is declared before the inline calculation, the engine immediately assigns a default value to
      the attribute. As a result, any subsequent `preference()`
      rules are ignored because the engine treats the existing default value as an established
      selection and avoids overwriting it with the calculated value. Annotating the target
      attribute with `@(configurable=false)`) forces the engine
      to leave the variable as `null` until the calculation and
      preference rules are executed.

    

In this example, the engine processes `ShippingMethod`
      first and immediately assigns the default value "Standard" to it. Later, when the calculation
      for `totalWeight` returns a value high enough to require
      the “Freight” shipping method, the engine ignores this preference rule because the `ShippingMethod` variable is already bound to "Standard".

    

```
type Order : LineItem {
    int quantity = [1..100];
    int weightPerUnit = [10..50];

    // Problem: Engine assigns "Standard" immediately during initialization
    @(defaultValue = "Standard")
    string ShippingMethod = ["Standard", "Freight"];

    // Calculated Attribute via Inline Expression

    // The calculation happens after the default is already set
    int totalWeight = quantity * weightPerUnit;

    // This rule is ignored because ShippingMethod is already bound to "Standard"
    preference(totalWeight > 1000 -> ShippingMethod == "Freight");
}
```

    

In this example, using the `@(configurable=false)`
      annotation ensures the `ShippingMethod` attribute remains
      as `null` until the calculation completes and the rules
      execute.

    

#### Note

Provide a second preference rule for the fallback condition (else)
      to ensure a value is always set.

    

```
type Order : LineItem {
    int quantity = [1..100];
    int weightPerUnit = [10..50];

    // Solution: Prevent premature default assignment
    @(configurable=false)
    string ShippingMethod = ["Standard", "Freight"];

    // Calculated Attribute via Inline Expression
    int totalWeight = quantity * weightPerUnit;

    // Rule 1: Handle the specific condition (high weight)
    preference(totalWeight > 1000 -> ShippingMethod == "Freight");

    // Rule 2: Handle the fallback (low weight)
    preference(totalWeight <= 1000 -> ShippingMethod == "Standard");
}
```
