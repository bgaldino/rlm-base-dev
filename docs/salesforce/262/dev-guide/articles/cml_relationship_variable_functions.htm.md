---
page_id: cml_relationship_variable_functions.htm
title: Relationship Variable Functions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_relationship_variable_functions.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_relationships.htm
fetched_at: 2026-06-09
---

# Relationship Variable Functions

CML variable functions are fundamental tools used to perform both aggregation
(summarizing data from related components) and complex mathematical calculations on attribute
values (variables) within a configuration model. These functions are crucial for enforcing
dimensional validity and calculating derived attributes.

You can use functions such as `count()`, `min()`, `max()`, `sum()` and `total()` to
calculate values from all variables with the same name in the descendants of the current
type. Aggregate functions are used primarily as relationship attributes within a relation to
calculate values across multiple instances of a component type (descendants).

| Function | Purpose | CML Keyword [Source] |
| --- | --- | --- |
| `count()` | Counts the number of component instances within a relationship that match a specific logical condition. | `count` |
| `max() / min()` | Returns the maximum or minimum value of an attribute found across all instances in a relationship. | `max, min` |
| `sum()` | Calculates the sum of a specific numeric variable across all instances in a relationship. Note: executes multiplication of a variable value by a product quantity. | `sum` |
| `total()` | Calculates the sum of a specific numeric variable across all instances in a relationship. Note: Unlike the sum() function, does not execute multiplication of a variable value by line item quantity. | `total` |

## Example: Using Aggregate Functions

```
type LineItem;
type GeneratorSet : LineItem {
relation modelclassification : ModelClassification {
sumPowerKW = sum(powerKW);
maxPowerKW = max(powerKW);
highPowerModelsAmount = count(powerKW > 500);
}
relation warranties : Warranty  {
totalCoverageDays = total(coverageDays);
}
constraint(modelclassification.sumPowerKW > 2500 && modelclassification.sumPowerKW < 3500);
message(true, "The maximum `powerKW` from selected GeneralModels is: {}", modelclassification.maxPowerKW);
constraint(warranties[Warranty] == modelclassification.highPowerModelsAmount);
message(true, "Effective Warranty coverage days: {}", warranties.totalCoverageDays);
}
type ModelClassification : LineItem {
int powerKW = [900, 1750, 2500];
}
type GeneralModel1750 : ModelClassification {
int powerKW = 1750;
}
type GeneralModel2500 : ModelClassification {
int powerKW = 2500;
}
type GeneralModel900 : ModelClassification {
int powerKW = 900;
}
type Warranty {
int coverageDays;
}
type Warranty_PRP : Warranty {
int coverageDays = 50;
}
type Warranty_DCC : Warranty {
int coverageDays = 100;
}
type Warranty_ESP : Warranty {
int coverageDays = 200;
}
```

## sum()

In the example, the `sum()` function aggregates the
`powerKW` variable values of the selected products in
the `modelClassification` relationship. The model
includes a constraint that enforces the selection rule based on the calculated total: the
`sum` of `powerKW`
for the selected products must be between 2500 and 3500.

```
constraint(modelclassification.sumPowerKW > 2500 && modelclassification.sumPowerKW < 3500);
```

As a result, the engine selects two products from the `modelClassification` relation (`GeneralModel1750` and `GeneralModel900`),
since their calculated sum of `powerKW` values (2650)
satisfies the constraint.

## max()

In the example, the `max()` function returns the maximum
`powerKW` variable value among the selected products in
the `modelClassification` relationship. The model defines
a message that displays the maximum `powerKW` value in
the Product Configurator.

```
message(true, "The maximum `powerKW` from selected GeneralModels is: {}", modelclassification.maxPowerKW);
```

As a result, because the previously described `sum()`
function and constraint selected two products (`GeneralModel1750` and `GeneralModel900`), the
maximum returned value is 1750.

## count()

In the example, the `count()` function calculates the
amount of selected `modelClassification` relationship
products that contain the `powerKW` variable value
greater than 500. The model includes a constraint that enforces the selection of `warranties` product for each `GeneralModel` counted by the function.

```
constraint(warranties[Warranty] == modelclassification.highPowerModelsAmount);
```

As a result, based on the previous `sum()` description,
the engine selects two products (`GeneralModel1750` and
`GeneralModel900`). Since both products meet the
count() condition (`powerKW` > 500), the engine adds
one of the warranties product with quantity 2.

## total()

In the example, the `total()` function aggregates the
values of the `coverageDays` variable for the selected
products of the `warranties` relationship. The model
defines a message that displays the calculated total in the Product Configuration.

```
message(true, "Effective Warranty coverage days: {}", warranties.totalCoverageDays);
```

As a result, based on previously described `count()`
example, the system selects one of the `warranties`
product (e.g., `Warranty_DCC`) with a quantity of 2 and
calculates the total value of its `coverageDays` variable
(100).

A key difference between `total()` and `sum()` functions is that for `total()` the engine ignores the `warranties`
product quantity. The system does not multiply the quantity of the selected warranty by the
`coverageDays` variable value when computing the
overall total.

See also [Arithmetic Calculations and Functions](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.") and examples [here](./cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm.md "Constraint Modeling Language (CML) must accurately calculate the total sum or aggregate of specific attributes like quantity or userCount across child components, especially in complex configurations requiring group-level aggregation").
