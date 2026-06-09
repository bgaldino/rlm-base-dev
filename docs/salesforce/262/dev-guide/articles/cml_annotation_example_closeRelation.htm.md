---
page_id: cml_annotation_example_closeRelation.htm
title: closeRelation Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_closeRelation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# closeRelation Annotation

closeRelation is a CML annotation that controls addition of new line items to the
relationship by the engine.

| Annotation | `closeRelation` |
| --- | --- |
| Applicable to | Relationship |
| Value Type/Values | true, false |
| Description | If `closeRelation` is not specified, the engine sets it implicitly as false for the relationship.  If `closeRelation` is specified as true, the engine prevents the addition of new line items to the relationship.  If `closeRelation` is specified as false, the engine allows the addition of new line items to the relationship. |

## Example 1

In this example, the `closeRelation` annotation isn’t
specified for the relationship (`mainalternatorclassification`). The model contains the constraint.

```
type LineItem;
type GeneratorSet : LineItem { 
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    relation mainalternatorclassification : MainAlternatorClassification;
    constraint(dutyRating == "Continuous Power (COP)" -> mainalternatorclassification[Alternator_240] >= 1);
}
type MainAlternatorClassification : LineItem;
type Alternator_220 : MainAlternatorClassification;
type Alternator_440 : MainAlternatorClassification;
type Alternator_240 : MainAlternatorClassification;
```

## Example 2

In this example, the `closeRelation`annotation is
defined as `false` for the relationship (`mainalternatorclassification`). The model contains the
constraint.

```
type LineItem;
type GeneratorSet : LineItem {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    @(closeRelation = false)    
    relation mainalternatorclassification : MainAlternatorClassification;
    constraint(dutyRating == "Continuous Power (COP)" -> mainalternatorclassification[Alternator_240] >= 1);
}
type MainAlternatorClassification : LineItem;
type Alternator_220 : MainAlternatorClassification;
type Alternator_440 : MainAlternatorClassification;
type Alternator_240 : MainAlternatorClassification;
```

## Example Description and Configurator Result

In example 1, the `mainalternatorclassification`
relation is not specified with the `closeRelation`
annotation, but the system considers it as `false` by
default. In example 2, the relation is explicitly defined with `false`. As a result, if the user updates the `dutyRating` variable to `"Continuous Power
(COP)"`, the system adds the `Alternator_240` product according to annotation and constraint logic and allows
addition of other products from the `mainalternatorclassification` relation (`Alternator_220,Alternator_440`). The system does not allow to unselect the
`Alternator_240` product specified in the constraint
while the `"Continuous Power (COP)"` is
selected. If the user updates the `dutyRating` variable
to another value (For example, `Emergency Standby Power
(ESP)"`), the engine removes the `Alternator_240`product, but the user can add/select/unselect all products from the relationship
manually.

## Example 3

In this example, the `closeRelation` annotation is
specified as `true` for the relationship (`mainalternatorclassification`). The model contains the
constraint

```
type LineItem;
type GeneratorSet : LineItem {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    @(closeRelation = true)    
    relation mainalternatorclassification : MainAlternatorClassification;
    constraint(dutyRating == "Continuous Power (COP)" -> mainalternatorclassification[Alternator_240] >= 1);
}
type MainAlternatorClassification : LineItem;
type Alternator_220 : MainAlternatorClassification;
type Alternator_440 : MainAlternatorClassification;
type Alternator_240 : MainAlternatorClassification;
```

In example 3, the `mainalternatorclassification`
relation is specified with the `closeRelation` annotation
as `true`. As a result, if a user updates the dutyRating
variable to `"Continuous Power (COP)"`, the
engine resets it back to `"Emergency Standby Power
(ESP)"` to prevent adding the `Alternator_240` product according to the annotation. The user can add all `mainalternatorclassification` products manually (including the
`Alternator_240` product specified in the
constraint).

Table 1. closeRelation Configuration Settings

| Associated Example | Product Group Structure | Applicable to | "closeRelation" annotation | User Action | Engine Action | UI Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| N/A | Individual product | Relationship | not specified | Change variable value specified in constraint condition | Add the product according to the constraint. Allow addition of other products to the relationship | Display product specified in constraint as pre-selected: if a User unselects it, the product returns back to selected state.  User can select other products from the relationship |
| N/A | Individual product | Relationship | TRUE | Change variable value specified in constraint condition | Reset the variable value back to the default value to avoid addition the relation product specified in the constraint | Products from the relation are not added or selected (including the product specified in constraint). User can manually select any products from the relationship |
| N/A | Individual product | Relationship | FALSE | Change variable value specified in constraint condition | Add the product according to the constraint. Allow addition of other products to the relationship | Display product specified in constraint as pre-selected: if a User unselects it, the product returns back to selected state.  User can select other products from the relationship |
| Example 1 | Product Classification | Relationship | not specified | Change variable value specified in constraint condition | Add the product according to the constraint. Allow addition of other products to the relationship from browse products pop up | Display product specified in constraint as pre-selected: if a User unselects it, the product returns back to selected state.  User can add other products from the relationship in browse products pop up |
| Example 2 | Product Classification | Relationship | FALSE | Change variable value specified in constraint condition | Add the product according to the constraint. Allow addition of other products to the relationship from browse products pop up | Display product specified in constraint as pre-selected: if a User unselects it, the product returns back to selected state.  User can add other products from the relationship in browse products pop up |
| Example 3 | Product Classification | Relationship | TRUE | Change variable value specified in constraint condition | Reset the variable value back to the default value to avoid addition the relation product specified in the constraint | Products from the relation are not added or selected (including the product specified in constraint). User can manually browse and add any products from the relationship |
