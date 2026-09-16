---
page_id: cml_type_annotations.htm
title: Type Annotations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_type_annotations.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_types.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Type Annotations

You can annotate types to add information. Type annotations are metadata applied to a
    type declaration to provide instructions to the constraint engine regarding how instances of
    that type should be handled, instantiated, or used in the configuration structure.

    
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

- 
- 
- 

            

            
              

              

              

            

          

        
| Annotation | Possible Values | Description |
| --- | --- | --- |
| virtual | true, false | If `true`, specifies whether the indicated type refers to the transaction header (such as Quote or Order) or to a logical container (sub group of the Quote or Order). If the value is `false`, then it’s the default behavior for types and doesn’t need to be explicitly specified. |
| groupBy | Variable name | Used with `virtual = true`, the `groupBy` annotation organizes child products—the individual instances populating a relationship—into virtual containers based on a shared attribute value. See [Relationships](./cml_relationships.htm.md) and the [Grouping Generators by Voltage example](./cml_core_concept_examples.htm.md) . |
| maxInstanceQty | Integer | Specifies the maximum cardinality for a component in a group. See [Group Type](./cml_group_type.htm.md). |
| minInstanceQty | Integer | Specifies the minimum cardinality for a component in a group. See [Group Type](./cml_group_type.htm.md). |
| source | String | Specifies the data source defined in the model. |
| split | true, false, none | Specifies whether the type should be split or not. If `split=true`, there can be multiple instances of the type, and the quantity of each instance is always 1. If `split=false`, there is only one instance in the relationship. If the user adds more instances, the engine adds more quantity to the existing instance. If `split=none` (the default), there are multiple instances of the same type in the relationship, with different quantities. The `split=true` annotation isn't supported for child products within a dynamic bundle. See examples [here](./cml_annotation_examples.htm.md). |
| sharingcount | Integer | Specifies the maximum number of times a single instance of a specific type can be shared or reused across different relationships within the configuration model. This annotation is used in conjunction with the @(`split=true`) annotation. When a type is marked for splitting, the constraint engine can process multiple instances in parallel to improve performance. The `sharingCount` tells the engine exactly how many times it can "split" or reuse that instance to satisfy the configuration requirements without generating entirely new, unique instances. It's a critical tool for managing large-scale configurations (for example, models with over 1,000 components). By setting a sharing limit, you reduce the number of variables the engine must instantiate, which helps prevent performance degradation and system timeouts.The `sharingCount` annotation works with the @(`sharing=true`) annotation applied to Relations. The relation annotation enables the general capability to share components across instances, while the `sharingCount` on the child type sets the numerical limit for that behavior. See [Relationship Annotations](./cml_relationship_annotations.htm.md) and the [Sharing Accessories in a Generator Set example](./cml_core_concept_examples.htm.md). |

    

    

## Creating a Virtual Container (@virtual = true)

      
      

In this example, the `@virtual = true` annotation is
        applied to a logical container type, `System`, which is
        primarily used to define relationships. These relationships aggregate data across line items
        in the quote that forms a sub-group called `system`. See
          [Relationships](./cml_relationships.htm.md).

      

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
