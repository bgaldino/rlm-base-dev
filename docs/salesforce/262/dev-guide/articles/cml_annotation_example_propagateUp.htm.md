---
page_id: cml_annotation_example_propagateUp.htm
title: propagateUp Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_propagateUp.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# propagateUp Annotation

`propagateUp` is a Constraint Modeling Language
(CML) annotation that controls aggregation propagation between children and parent
elements.

| Annotation | `propagateUp` |
| --- | --- |
| Applicable to | Relationship |
| Value Type/Values | true, false |
| Description | If propagateUp is not specified, the engine sets it implicitly as false for the relationship.   - If the propagateUp annotation is specified as true, the engine aggregates   values from children to parent elements (upward propagation). The engine cannot   modify this value from the parent level (e.g. via constraint), so the children   relation domain will not be affected. - If the propagateUp is specified as false, both upward and downward   propagations are applicable. The engine aggregates values from children to   parent elements (upward propagation). Meanwhile the engine can modify this value   (e.g. via constraint) from the parent level. The value is propagated downward   and might affect the relation domain (downward propagation). |

## Example 1

In this example, the `propagateUp` annotation is not specified for the relationship (`warranties`). The model contains technical variable (`coverageDays`) and
constraint.

```
type GeneratorSet {

        relation warranties : Warranty {
        totalDays = sum(coverageDays);
    }
    constraint(warranties.totalDays <= 299);
}

type Warranty {
    int coverageDays = 100;
}

type Warranty_PRP : Warranty;

type Warranty_DCC : Warranty;

type Warranty_ESP : Warranty;
```

## Example 2

In this example, the `propagateUp` annotation is defined as `false`
for the relationship (`warranties`). The model contains
technical variable (coverageDays) and
constraint.

```
type GeneratorSet {

        @(propagateUp = false)
        relation warranties : Warranty {
        totalDays = sum(coverageDays);
    }
    constraint(warranties.totalDays <= 299);
}

type Warranty {
    int coverageDays = 100;
}

type Warranty_PRP : Warranty;

type Warranty_DCC : Warranty;

type Warranty_ESP : Warranty;
```

## Example Description and Configurator Result

In example 1, the `warranties` relation is not specified
with the propagateUp annotation, and the system considers it as `false` by default. In example 2, the relation is explicitly defined with a
`false` annotation value. Each product of the `warranties` relation is assigned with the technical `coverageDays` variable equalled to 100. The `totalDays` calculates the `coverageDays` sum of selected `warranties`
products. As a result, the system validates the constraint and relation domain in the
following way:

- The user selects one `warranties` product (e.g. `Warranty_PRP`). The system calculates the `totalDays` aggregated value for the relation (equal to 100).
  The system validates the constraint on the parent based on the calculated aggregation
  variable. The constraint is satisfied (100<= 299). The system also verifies the
  possibility to add extra products to the relation. The capacity of the constraint allows
  to add one more product to the relation, so the system will not reduce the relation
  domain.
- The user selects the second `warranties` product (e.g.
  `Warranty_DCC`). The system calculates the `totalDays` aggregated value for the relation (equal to 200).
  The system validates the constraint on the parent based on the calculated aggregation
  variable. The constraint is satisfied (200<= 299). The system verifies the possibility
  to add extra products to the relation. The capacity of the constraint (300<= 299) does
  not allow to add one more product to the relation, so the system will reduce the relation
  domain.
- The user unselects one of the selected `warranties` products
  (e.g. `Warranty_PRP`). The system calculates the
  `totalDays` aggregated value for the relation (equal
  to 100). The system validates the constraint on the parent based on the calculated
  aggregation variable. The constraint is satisfied (100<= 299). The system verifies the
  possibility to add extra products to the relation. The capacity of the constraint allows
  to add one more product to the relation, so the system will not reduce the relation domain
  (both `Warranty_DCC` and `Warranty_ESP` products are available for selection).

## Example 3

In this example, the `propagateUp` annotation is specified for the relationship (`warranties`) as `true`. The
model contains technical variable (`coverageDays`) and
constraint.

```
type GeneratorSet {

        @(propagateUp = true)
        relation warranties : Warranty {
        totalDays = sum(coverageDays);
    }
    constraint(warranties.totalDays <= 299);
}

type Warranty {
    int coverageDays = 100;
}

type Warranty_PRP : Warranty;

type Warranty_DCC : Warranty;

type Warranty_ESP : Warranty;
```

## Example Description and Configurator Result

In example 3, the relation is specified with `propagateUp` annotation as `true` value. Each
product of the `warranties` relation is assigned with the
technical `coverageDays` variable equalled to 100. The
`totalDays` calculates the `coverageDays` sum of selected `warranties`
products. As a result, the system validates the constraint and relation domain in the
following way:

The user selects one `warranties` product (e.g. `Warranty_PRP`). The system calculates the `totalDays` aggregated value for the relation (equal to 100).
The system validates the constraint on the parent based on the calculated aggregation
variable. The constraint is satisfied (100<=299);

The user selects the second `warranties` product (e.g.
`Warranty_DCC`). The system calculates the `totalDays` aggregated value for the relation (equal to 200).
The system validates the constraint on the parent based on the calculated aggregation
variable. The constraint is satisfied (200<=299);

The user selects the third `warranties` product (e.g.
`Warranty_ESP`). The system calculates the `totalDays` aggregated value for the relation (equal to 300).
The system validates the constraint on the parent based on the calculated aggregation
variable. The constraint is not satisfied (300<=299). The system rejects the selection of
one of the warranties products to satisfy the constraint.

As a best practice, use the `propagateUp = true` for
models with few relationships and rare constraint violations, since it minimizes propagation
work and avoids extra domain updates. Meanwhile, set the `propagateUp = false` for large product structures or frequent violations, since
bidirectional propagation prevents invalid states early and reduces expensive
backtracking.

## propagateUp Configuration Settings

Table 1. propagateUp Configuration Settings

| Associated Example | Product Group Structure | Applicable to | "propagateUp" annotation | User Action | Engine Action | UI Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| Example 1 | Individual product | Relationship | not specified | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint, limitation of the relation domain when the constraint capacity is used up | Displays the selected products. When constraint capacity is used up, in addition to the selected products the limited list of the available to be added products will be displayed(if any) |
| Example 2 | Individual product | Relationship | FALSE | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint, limitation of the relation domain when the constraint capacity is used up | Displays the selected products. When constraint capacity is used up, in addition to the selected products the limited list of the available to be added products will be displayed(if any) |
| Example 3 | Individual product | Relationship | TRUE | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint, rejection of the user selection when the constraint validation is failed | Displays the selected products. No limitations for the list of available products |
| N/A | Product Classification | Relationship | not specified | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint. The engine might replace one of the previously selected products with a newly selected | Displays the selected products. No limitations for the list of available products in the browse popup for the classification |
| N/A | Product Classification | Relationship | FALSE | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint. The engine might replace one of the previously selected products with a newly selected | Displays the selected products. No limitations for the list of available products in the browse popup for the classification |
| N/A | Product Classification | Relationship | TRUE | Selects or deselects the products | Calculates the aggregation variable value on the relation, validation of the constraint, rejection of the user selection when the constraint validation is failed | Displays the selected products. No limitations for the list of available products in the browse popup for the classification |
