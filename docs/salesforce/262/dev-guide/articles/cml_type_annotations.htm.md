---
page_id: cml_type_annotations.htm
title: Type Annotations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_type_annotations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_types.htm
fetched_at: 2026-06-09
---

# Type Annotations

You can annotate types to add information. Type annotations are metadata applied to a
type declaration to provide instructions to the constraint engine regarding how instances of
that type should be handled, instantiated, or used in the configuration structure.

| Annotation | Possible Values | Description |
| --- | --- | --- |
| virtual | true, false | If `true`, specifies whether the indicated type refers to the transaction header (such as Quote or Order) or to a logical container (sub group of the Quote or Order). If the value is `false`, then it’s the default behavior for types and doesn’t need to be explicitly specified. |
| groupBy | Variable name | Used with `virtual = true`, the `groupBy` annotation organizes child products—the individual instances populating a relationship—into virtual containers based on a shared attribute value.  See [Relationships](./cml_relationships.htm.md "Relationships in Constraint Modeling Language (CML) define how different product types are associated with each other, forming the structural hierarchy of a product bundle. Relationships are also referred to as ports.") and the [Grouping Generators by Voltage example](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.") . |
| maxInstanceQty | Integer | Specifies the maximum cardinality for a component in a group. See [Group Type](./cml_group_type.htm.md "In Constraint Modeling Language (CML), a Group Type is used to logically containerize related components within a bundle configuration, primarily when product component groups are imported from Product Catalog Management (PCM)."). |
| minInstanceQty | Integer | Specifies the minimum cardinality for a component in a group. See [Group Type](./cml_group_type.htm.md "In Constraint Modeling Language (CML), a Group Type is used to logically containerize related components within a bundle configuration, primarily when product component groups are imported from Product Catalog Management (PCM)."). |
| source | String | Specifies the data source defined in the model. |
| split | true, false, none | Specifies whether the type should be split or not.   - If `split=true`, there can be multiple   instances of the type, and the quantity of each instance is always 1. - If `split=false`, there is only one   instance in the relationship. If the user adds more instances, the engine adds   more quantity to the existing instance. - If `split=none` (the default), there are   multiple instances of the same type in the relationship, with different   quantities.  The `split=true` annotation isn't supported for child products within a dynamic bundle. See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| sharingcount | Integer | Specifies the maximum number of times a single instance of a specific type can be shared or reused across different relationships within the configuration model.  This annotation is used in conjunction with the @(`split=true`) annotation. When a type is marked for splitting, the constraint engine can process multiple instances in parallel to improve performance.  The `sharingCount` tells the engine exactly how many times it can "split" or reuse that instance to satisfy the configuration requirements without generating entirely new, unique instances. It's a critical tool for managing large-scale configurations (for example, models with over 1,000 components). By setting a sharing limit, you reduce the number of variables the engine must instantiate, which helps prevent performance degradation and system timeouts.The `sharingCount` annotation works with the @(`sharing=true`) annotation applied to Relations. The relation annotation enables the general capability to share components across instances, while the `sharingCount` on the child type sets the numerical limit for that behavior.  See [Relationship Annotations](./cml_relationship_annotations.htm.md "You can annotate relationships by using annotations, such as configurable, allowNewInstance, closeRelation, sourceContextNode, and so on.") and the [Sharing Accessories in a Generator Set example](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on."). |

## Creating a Virtual Container (@virtual = true)

In this example, the `@virtual = true` annotation is
applied to a logical container type, `System`, which is
primarily used to define relationships. These relationships aggregate data across line items
in the quote that forms a sub-group called `system`. See
[Relationships](./cml_relationships.htm.md "Relationships in Constraint Modeling Language (CML) define how different product types are associated with each other, forming the structural hierarchy of a product bundle. Relationships are also referred to as ports.").

```
@(virtual = true)
type System {
// This relation gathers all GeneratorSet line items on the sales transaction
@(sourceContextNode = "SalesTransaction.SalesTransactionItem")
relation generators : GeneratorSet[0..10];
// This variable aggregates the surge load (calculated inside GeneratorSet) from all collected generators
int totalQuotedLoad = generators.sum(surgeLoadKW);
}
type GeneratorSet {
// The attribute calculated here is aggregated in the virtual 'System' type above
@(configurable = false)
int requiredKW = [101..10000];
string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)", "Emergency Standby Power (ESP)"];
decimal(2) surgeLoadKW = requiredKW * 1.25;
}
```
