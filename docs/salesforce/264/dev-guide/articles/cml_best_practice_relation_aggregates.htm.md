---
page_id: cml_best_practice_relation_aggregates.htm
title: "Relation Aggregates: Stabilize Preferences Using Staged Variables"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_relation_aggregates.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Relation Aggregates: Stabilize Preferences Using Staged Variables

To improve solver stability and prevent backtracking, stage relation aggregates through
    local variables and state anchors instead of referencing them directly in
    preferences.

    

To improve solver stability and prevent backtracking, avoid referencing relation aggregates
      directly within preferences when the preferences also influence the same relation. Instead,
      stage these aggregates through local variables and state anchors.

    

In this example, the preferences and the calculated quantity depend directly on live
      relation aggregates.

    

```
relation ml : ModelTraining {
   totalNumSubscriptions = total(NumSubscriptions);
   subCount = count(Sublicense == true);
}
preference(ml[ModelTraining] > 0 && ml.subCount == 0 -> ml[ModelTraining] == parentQty);
preference(ml[ModelTraining] > 0 && ml.subCount > 0 -> ml[ModelTraining] == calculatedQuantity);
constraint(calculatedQuantity == ((ml.totalNumSubscriptions + 99) / 100) * 100);
```

    

When the solver evaluates preferences that depend directly on a relation's own aggregates,
      it creates a tight feedback loop:

    

Relation Quantity ⟶ Relation Aggregates ⟶ Preference Guards/Targets ⟶ Relation Quantity
      (loop repeats)

    

The feedback loop can cause the solver to oscillate or backtrack repeatedly before finding
      a stable solution.

    

This example shows the stabilized pattern. It introduces staged variables that act as
      anchors to separate the relation aggregates from the preference logic.

    

```
relation ml : ModelTraining {
    totalNumSubscriptions = total(NumSubscriptions);
    subCount = count(Sublicense == true);
}

// Stage 1: Convert relation conditions into stable booleans
boolean hasSub;
constraint(hasSub <-> (ml.subCount > 0));

// Stage 2: Copy relation aggregates into local variables
int localTotalNumSubscriptions;
constraint(localTotalNumSubscriptions == ml.totalNumSubscriptions);

// Stage 3: Perform calculations by using the local variables
int calculatedQuantity;
constraint(calculatedQuantity == ((localTotalNumSubscriptions + 99) / 100) * 100);

// Stage 4: Use the staged variables in the preferences
preference(ml[ModelTraining] > 0 && hasSub == false -> ml[ModelTraining] == parentQty);
preference(ml[ModelTraining] > 0 && hasSub == true -> ml[ModelTraining] == calculatedQuantity);
```

    

With this pattern, instead of solving everything simultaneously, the solver logic processes
      a pipeline:

    

Relation ⟶ Aggregates ⟶ Anchored State/Local Variables ⟶ Derived Calculations ⟶
      Preferences

    

This process reduces oscillation and makes the solving path more deterministic.
