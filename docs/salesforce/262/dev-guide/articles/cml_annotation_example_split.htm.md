---
page_id: cml_annotation_example_split.htm
title: split Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_split.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# split Annotation

`split` is a Constraint Modeling Language (CML)
annotation that specifies whether the instances of the type should be split or not.

| Annotation | `split` |
| --- | --- |
| Applicable to | Type |
| Value Type/Values | true, false |
| Description | If split isn’t specified, there are multiple instances of the same type in the relationship with different quantities.  If the split is specified as `true`, there can be multiple instances of the type, and the quantity of each instance is always 1.  If the split is specified as `false`, there is only one instance in the relationship.  If the user adds more instances, the engine adds more quantity to the existing instance. |

## Example 1

In this example, the split annotation isn’t specified for the type (Model).

```
type FESBAGeneratorSet {
    relation models : Model;
}
type Model;
```

## Example Description and Configurator Result

In this example, the system allows the multiple instances of the Model type with different quantities defined by the user.

## Example 2

In this example, the split annotation is specified as
`true` for the type
(Model).

```
type FESBAGeneratorSet {
    relation models : Model;
}
@(split = true)
type Model;
```

## Example Description and Configurator Result

In this example, the annotation `split = true` specifies
that the multiple Model instances are split into individual items with fixed quantity 1.

## Example 3

In this example, the split annotation is specified as
`false` for the type
(Model).

```
type FESBAGeneratorSet {
    relation models : Model;
}
@(split = false)
type Model;
```

Use `@(split=false)` when the
line item record must persist across configuration changes and record continuity matters for
your business process. The `@(split=false)` annotation
prevents the configurator from deleting and recreating existing line item records when the
quantity or selection changes. When you apply `@(split=false)`, the configurator updates the quantity on the existing record
instead of replacing it with a new one. This preserves the record ID and any data associated
with it.

## Example Description and Configurator Result

In this example, the system allows one instance of the Model type with different quantity defined by the user.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

If there are multiple products of type Model (for example, `FESBA 900kW` and `FESBA
1500kW`), the user can add both models to the configuration and adjust the
quantity for each one. However, the user can’t add additional separate instances of the same
product (for example, to configure unique instances with different variable values).

## split Configuration Settings

Table 1. split Configuration Settings

| Product Group Structure | "split" annotation | Engine Action | user Action | UI Behavior |
| --- | --- | --- | --- | --- |
| Product Classification | TRUE | Add multiple products | N/A | N/A |
| Product Classification | TRUE | N/A | Selecting or adding the product multiple times manually | Multiple instances created (qty = 1 each). User can add more instances, but can't change quantity per instance. |
| Product Classification | FALSE | Add multiple products | N/A | One instance created with qty > 1. User can change the quantity of this instance, but can't add more instances. |
| Product Classification | FALSE | N/A | Selecting or adding the product multiple times manually | One instance created with qty = 1. User can change the quantity of this instance, but can't add more instances. |
| Product Classification | (empty) | Add multiple products | N/A | One instance created with qty > 1. User can change quantity and can add more instances. |
| Product Classification | (empty) | N/A | Selecting or adding the product multiple times manually | One instance created with qty = 1. User can change quantity and can add more instances. |
| Individual Product | TRUE | Add multiple products | N/A | Multiple line items created, but Configurator displays only one instance. Users cannot modify quantity for that instance. |
| Individual Product | TRUE | N/A | Selecting or adding the product manually | One instance created with qty = 1. Users cannot change quantity. |
| Individual Product | FALSE | Add multiple products |  | One instance created with qty > 1. Users can't modify quantity for that instance. |
| Individual Product | FALSE | N/A | Selecting or adding the product manually | One instance created with qty = 1. Users can modify quantity for that instance. |
| Individual Product | (empty) | Add multiple products |  | One instance created with qty > 1. Users can't modify quantity for that instance. |
| Individual Product | (empty) | N/A | Selecting or adding the product manually | One instance created with qty = 1. Users can modify quantity for that instance. |
