---
page_id: cml_business_centric_cml_examples.htm
title: Business-Centric CML Examples
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_business_centric_cml_examples.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm
fetched_at: 2026-06-09
---

# Business-Centric CML Examples

These Constraint Modeling Language (CML) structures implement quantity aggregation and
resolve calculation dependencies.

## Example 1: Derived Aggregates (Total Quantity or Sum)

This CML example shows how to model bundle rollups by separating aggregation from validation, ensuring correct calculation order, solver stability, and business-rule consistency

```
type LineItem;
type GeneratorSet : LineItem {
  int totalItemPowerKW = modelclassification.totalPowerKW;
  // Aggregate `powerKW`
  relation modelclassification : ModelClassification[0..10] {
    totalPowerKW = sum(powerKW);
  }
  message(true, "GeneratorSet totalItemPowerKW = {} kW (calculated roll-up). Sum of selected ModelClassification powerKW values = {} kW.", totalItemPowerKW, modelclassification.totalPowerKW);
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
```

## Example Description and Configurator Result

In example 1, the `GeneratorSet` type contains the
`totalItemPowerKW` variable that is assigned with the
`totalPowerKW`. The model specifies a relationship
based on the product classification (`modelClassification`). This relationship includes aggregation using the sum()
function that calculates the `totalPowerKW` from the
products selected in the `modelClassification` during
bundle configuration. The model contains a message for displaying the `totalItemPowerKW` with the `modelClassification.totalPowerKW` on the Product Configuration.

```
message(true, "GeneratorSet totalItemPowerKW = {} kW (calculated roll-up). Sum of selected ModelClassification powerKW values = {} kW.", totalItemPowerKW, modelclassification.totalPowerKW);
```

As a result, the engine calculates the `totalPowerKW` of
user selected products in the `modelClassification` and
assigns this value to the `totalItemPowerKW`. The system
displays both values in the information message on the Product Configuration.

## Example 2: Resolving Circular Dependencies

This pattern breaks unsolvable loops by enforcing unidirectional data flow (Parent dictates Child quantity based on Child aggregates).

```
type LineItem;
type GeneratorSet : LineItem {
  // RELATION: THE "READ" PHASE
  // Data flows UP from children to the parent via the port attribute
  relation voltageclassification : VoltageClassification[1..10] {
    sumOfChildPower = total(power);
  }
  // Explicit domain ensures the solver initializes correctly for calculations
  decimal(2) totalDistributionValue = [0.00..1000.00];
  // CONSTRAINT 1: THE "CALCULATION" PHASE
  // @(sequence = 1) ensures the engine reads child data and calculates first
  @(sequence = 1)
  constraint calcTotalDistribution(totalDistributionValue == voltageclassification.sumOfChildPower / 100);
  // CONSTRAINT 2: THE "WRITE/ENFORCE" PHASE
  // @(sequence = 2) ensures this happens last to push values DOWN to children
  @(sequence = 2)
  constraint setChildQuantity(voltageclassification[VoltageClassification] == totalDistributionValue * 2);
}
type VoltageClassification : LineItem {
  int power = [1..100];
}
type VoltageConnection_220_380 : VoltageClassification;
type VoltageConnection_240_416 : VoltageClassification;
type VoltageConnection_255_440 : VoltageClassification;
```

## Example Description and Configurator Result

In example 2, the relationship includes aggregation using the `total()` function that calculates the `sumOfChildPower` from the selected products in the `voltageclassification`. The `GeneratorSet`
type contains the `totalDistributionValue` with the
explicit domain ([0.00..1000.00]). The model contains two constraints with corresponding
`@sequence` annotation to enforce the logical order for
calculation of the `calcTotalDistribution` (using child
products data) and defining the quantity for the `voltageclassification` child items.

## Example 3: Grouped Aggregation (Sum of Users Across Regions)

This advanced pattern uses the `@(groupBy=attribute)`
annotation to create virtual components (`RegionGroup`)
for aggregation, referencing the source data relation in the parent type (`SubscriptionOrder.licenses`) using the `sourceContextNode` annotation.

```
// 1. Base Product Type (e.g., Regional License)
type RegionalLicense {
  int regionId = [0..100]; // Attribute for grouping
  int userCount = [0..100];
}
// 2. Virtual Group Type (Performs grouping and user sum)
@(split=true, virtual=true, groupBy=regionId)
type RegionGroup {
  int regionId;
  int groupTotalUsers; // Sum of userCount for this region
  // Relation to licenses matching this region group
  @(sourceContextNode="SubscriptionOrder.licenses")
  relation licenses: RegionalLicense[0..100];
  // Constraint: Calculate the aggregate user count within this group
  constraint(groupTotalUsers == licenses.sum(userCount));
}
// 3. Parent Order Management (Aggregates all region totals)
@(virtual=true)
type SubscriptionOrder {
  // Overall total users is calculated by referencing the group totals
  int totalUsers = regionGroups.groupTotalUsers;
  relation licenses: RegionalLicense[0..500];
  relation regionGroups: RegionGroup[1..10];
}
```

## Example Description and Configurator Result

In example 3, the `licenses` relationship that is
brought as an external source by `@(sourceContextNode="SubscriptionOrder.licenses")`, includes an aggregation using
the `sum()` function that calculates the `groupTotalUsers` from the selected products in the `RegionalLicense`. The `RegionGroup` type contains the `groupTotalUsers` variable that serves the aggregation. The `SubscriptionOrder` type contains the aggregate metric `totalUsers` which is calculated by summing all `groupTotalUsers`. The model contains one core constraint on
`RegionGroup` to enforce that `groupTotalUsers` equals the sum of all `userCount` from its member licenses.
