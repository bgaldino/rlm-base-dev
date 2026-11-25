---
page_id: cml-relationship-annotations
title: Relationship Annotations
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-relationship-annotations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-relationships
legacy_page_id: cml_relationship_annotations.htm
fetched_at: 2026-11-25
---

# Relationship Annotations

You can annotate relationships by using annotations, such as configurable, allowNewInstance, closeRelation, sourceContextNode, and so on.

You can annotate relationships, as in this example, with `configurable=true`.

```
// 1. Define the target type
type Component;
// 2. Define the parent type to hold the relation
type System {
// 3. Add the relation with cardinality and proper nesting
@(configurable = true)
relation components : Component[0..10];
}
```

Here are the details of relationship annotations.

| Annotation | Values | Description |
| --- | --- | --- |
| allowNewInstance | true, false | Enables require rule constraints to work on relationships that are otherwise closed. Must be set to true to enable require rule constraints on closed relationships. |
| closeRelation | true, false | If the value is true, prevents the addition of new line items to the relationship. false is the default value and allows the addition of new line items to the relationship. See examples [here](./cml-annotation-examples.md). |
| compNumberVar | true, false | Avoids creating a component number variable if it is set to false. |
| disableCardinalityConstraint | true, false | Disable cardinality constraint in the relationship to optimize the performance. |
| domainComputation | true, false | `domainComputation` is a Constraint Modeling Language (CML) annotation that specifies how the domain of a model element is determined, either by using a fixed domain or by computing the domain dynamically during configuration. If `domainComputation` is not explicitly specified, the engine sets it implicitly as `true` for the relationship. If the domainComputation is specified as `true`, the relationship domain is dynamically determined based on the configuration and constraint logic. If the `domainComputation` is specified as `false`, the relationship domain is fixed. See examples [here](./cml-annotation-examples.md). |
| generic | true, false | Indicates if generic instance is allowed in the relationship or not. Generic instance is used to prompt the user that they need to select a product in the relationship. |
| noneLeafCardVar | true, false | Avoids creating cardinality variables for none leaf type (a node with no children) in the relationship to optimize the performance. |
| propagateUp | true, false | Aggregates values from child elements to parent elements. If propagateUp is not specified, the engine sets it implicitly as false for the relationship. If the propagateUp annotation is specified as true, the engine aggregates values from children to parent elements (upward propagation). The engine cannot modify this value from the parent level (e.g. via constraint), so the children relation domain will not be affected. If the propagateUp is specified as false, both upward and downward propagations are applicable. The engine aggregates values from children to parent elements (upward propagation). Meanwhile the engine can modify this value (e.g. via constraint) from the parent level. The value is propagated downward and might affect the relation domain (downward propagation). See examples [here](./cml-annotation-examples.md). |
| readOnly | true, false | Sets a relationship and all child relationships to read-only, to prevent the engine or user from modifying. |
| relatedAttributes | string value | `relatedAttributes` is a CML annotation that resets the domain to the original one for `domainComputation`. If `domainComputation` is not explicitly specified, the engine sets it implicitly as `true` for the relationship. If the `domainComputation` is specified as `true`, the relationship domain is dynamically determined based on the configuration and constraint logic. If the `domainComputation` is specified as `false`, the relationship domain is fixed. See examples [here](./cml-annotation-examples.md). |
| relatedRelationships | string value | Related relationships whose cardinality variables must be unbound for domain computation. |
| sequence | integer | Indicates the sequence in which the relationship is configured and executed. |
| sharing | true, false | Indicates if the relationship is shared or not. If the relationship is shared, the engine connects the instance from another relationship to this relationship instead of instantiating the instance in the relationship itself. |
| singleton | true, false | Indicates if all types in the relationship must be singleton or none. |
| source | string | Data source defined in the model. |
| sourceAttribute | Variable name in string | Sets the domain of the current relationship to the domain of the source attribute. |
| sourceContextNode | string | For cases that use a virtual container, specifies the path in the context service for the instances in the relationship. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-relationship-annotations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
