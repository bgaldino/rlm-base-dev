---
page_id: cml_relationships.htm
title: Relationships
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_relationships.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_core_concepts.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Relationships

Relationships in Constraint Modeling Language (CML) define how different product types
    are associated with each other, forming the structural hierarchy of a product bundle.
    Relationships are also referred to as ports.

    
      

Here’s a comprehensive overview of relationships, their syntax, purpose, and key features,
        particularly using examples relevant to the Generator Set model.

      

#### Note

When you import product relationships from PCM into a constraint
        model, don’t include product component groups. Importing with product component groups
        increases complexity and can cause performance degradation.

    

    

## Definition and Syntax of Relationships

      
      

Relationships define the one-to-many connections between a parent type (such as a bundle) and its component types (children).

      
        
- Keyword: The keyword used is `relation`.

        
- Syntax: A basic relationship declaration includes the relation name, the target type,
          and cardinality
          bounds.

```
relation <relation name> : <Target Type>[min..max] { /* Optional content */ }
```

        
- Purpose: Relationships represent the product structure in a bundle. For example, the
          root product (GeneratorSet) has relationships with its components (`MainAlternators`, `TemperatureSensors`).

      

      

#### Note

To avoid testing unnecessary value combinations and improve performance,
        specify the smallest required cardinality (quantity range).

    

    

## Set Maximum Relationship Size

The `maxRelationSize` property is the maximum cardinality for a
        single relationship in the constraint model. It controls how many instances of a child
        component can exist under one parent through the relationship.  The maximum value for
          `maxRelationSize` is 1073741824. The default value is
        9999. 

Use `maxRelationSize` to set a limit based
        on the number of instances you need for your business purposes. For example, if the most a
        customer can order of a child component is 200,000, set `maxRelationSize` to 200,000. An overly high cardinality limit increases the risk
        of unbound variables that cause the constraint engine to backtrack through the entire range
        to resolve a conflict. Use `maxRelationSize` with the
          `property`.

      

```
property maxRelationSize = 100000;                                                                  
 type Quote {                                                                             

   relation items : LineItem[0..99999999]; // cardinality uses this max

 }
```

The `maxRelationSize` property doesn’t
        limit these values:

        
- The number of relationship declarations in a type 

        
- The number of types in the constraint model

        
- The total component count across all relationships

      

    

## Omit Unnecessary Relationships

When using the [visual builder](https://help.salesforce.com/s/articleView?id=ind.product_configurator_use_the_visual_builder.htm&language=en_US) or the [CML editor](https://help.salesforce.com/s/articleView?id=ind.product_configurator_use_the_cml_editor.htm&language=en_US) to create a CML
        code for a bundle, the system by default imports all the relationships for the selected
        bundle from the structure defined in Product Catalog Management (PCM). In large and complex
        CML code, some of these relationships may not be relevant to any constraint and can be
        potentially omitted.

To enable import of a subset of bundle components, add this
        property at the top of the constraint model CML
        file.

```
property allowMissingRelations = "true";
```

If your PCM bundle contains many relations but your CML code defines only one, the engine
        validates the model, but often returns a configuration failure. at run time. By setting
          `allowMissingRelations = "true"`, you don’t have to
        define every relation found in the PCM (such as GeneralModels in the Relationship Ordering
        example) if they don’t require specific configuration logic in your CML file.

Here’s an example with the allowMissingRelations property.

```
// 1. Enable skipping of unneeded relations from the Product Catalog (PCM)
property allowMissingRelations = "true";

type ConciseGeneratorBundle  {
    // Define only the specific accessory needed for this logic
    relation enclosures : Enclosure;

    // A simple variable to trigger the logic
    int requiredKW = [100..5000];

    // Logic: High power requirements force a specific enclosure type
    // This omits other accessories like filters, batteries, and heaters [2, 3].
    constraint(requiredKW > 2000 -> enclosures[ReinforcedEnclosure] == 1, 
               "Power levels above 2000kW require a Reinforced Enclosure.");
}

// 2. Define the accessory and its specific subtype
type Enclosure ;
type ReinforcedEnclosure : Enclosure;

```

For more information, see [Constraints](./cml_constraints.htm.md).

To ensure stability at run time without the allowMissingRelations property, you must manually
        define every relation and type present in the PCM bundle, even if you don't intend to write
        logic for them. This creates large CML files with a high number of variables and components,
        which lead to performance degradation, and even timeout issues.

#### Note

We don’t recommend using the pattern in this example.

```
// EXPENSIVE FIX: Mirroring everything
type GeneratorSet {
    relation engineModels : EngineModel; // Unused in CML logic
    relation alternators : Alternator;    // Unused in CML logic
    relation fuelFilters : FuelFilter;    // Unused in CML logic
    relation starterMotors : StarterMotor; // Unused in CML logic
    relation enclosures : Enclosure;      // The only one we need
    // ... potentially 15+ more relations ...

    constraint(requiredKW > 2000 -> enclosures[ReinforcedEnclosure] == 1);
}
type Enclosure ;
type ReinforcedEnclosure : Enclosure;

```

    

## Skip Type Generation for Types with Many Mapped
        Products

When you create a constraint model for a product whose type is mapped to
        a large number of products, either directly or through product classifications , the
        constraint engine loads all mapped product data into the model during model fetch,
        regardless of whether those products are used in your CML. In catalogs with hundreds or
        thousands of mapped products, the loading process can significantly increase model fetch and
        execution time, causing timeouts. To load only the types that you explicitly declare in your
        constraint model and skip generating types from unmapped product data, add the `skipTypeGeneration` property at the top of the constraint
        model CML file.

```
property skipTypeGeneration = "true";

```

When you set `skipTypeGeneration = "true"`, the constraint
        engine skips type generation for all products not declared in the CML file, to optimize
        model storage. This property applies to types only and doesn't affect relationship loading
        or other model elements.

Use skipTypeGeneration = "true" when all
        of the following are true.

        
- A type in your constraint model is mapped to hundreds or thousands of products, either
          directly or through a product classification. 

        
- Your CML defines constraints for only a subset of those mapped products. 

        
- You experience slow load times or execution timeouts.

      

#### Note

Before you enable `skipTypeGeneration`, confirm that you explictly declare every type that your CML
        references in the constraint model. When you skip type generation, the constraint engine can
        only resolve types that it finds in your declarations. A referenced type that isn't declared
        causes an error when you try to save the model. As a best practice, use `skipTypeGeneration` only when your constraint model includes
        classification types. 

    

## Example: skipTypeGeneration with a Large Classification
        Catalog

In this example, a `GeneratorSet` product is mapped to many
        products through a classification. The CML enforces duty-rating and engine constraints, but
        only needs two component types. Setting `skipTypeGeneration =
          "true"` at the top of the constraint model prevents the constraint engine from
        loading mapped products that the model doesn't use.

```
// Skip loading all classification types from PCM.
// Only the types explicitly declared in this file are loaded.
property skipTypeGeneration = "true";
type GeneratorSet : LineItem {
   string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"];
   int requiredKW = [100..10000];
   relation engine : Engine[1..1];
   constraint(DutyRating == "Emergency Standby Power (ESP)" -> requiredKW >= 500,
              "Emergency Standby Power requires at least 500 kW.");
   constraint(DutyRating == "Prime Power (PRP)" -> engine[PrimePowerEngine] == 1,
              "Prime Power duty rating requires a Prime Power Engine.");
}
// Declare only the types this constraint model requires.
// Classification types not declared here are not loaded into the model.
type Engine;
type PrimePowerEngine : Engine;
type ContinuousPowerEngine : Engine;

```

    

## Order Keyword

      
      

The `order()` keyword is used within a `relation` declaration to define the specific sequence in which
        the constraint engine evaluates and attempts to instantiate the child subtypes available in
        that relationship. This controls the prioritization of component selection.

    

    

## Example: Relationship Ordering

      
      

```
// --- Component Subtypes (Specific Generator Models) ---
// Define a base type for generator models with a power attribute
type GeneralModel {
int powerKW = [0..3000]; // Explicit domain
}
// Specific subtypes that inherit from GeneralModel
type GeneralModel2500 : GeneralModel {
int powerKW = 2500;
}
type GeneralModel1750 : GeneralModel {
int powerKW = 1750;
}
type GeneralModel900 : GeneralModel {
int powerKW = 900;
}
// --- Parent Type (GeneratorSet) ---
type GeneratorSet {
// Required power defined by the parent (non-configurable)
@(configurable = false)
int requiredKW = [100..3000];
// Relation Declaration using order()
// Cardinality requires exactly one model to be selected.
// order() sets the selection priority (2500 KW model is checked before 1750 KW model).
relation GeneralModels : GeneralModel  order(GeneralModel2500, GeneralModel1750, GeneralModel900);
}
```

    

  

- 
**[Relationship Variable Functions](./cml_relationship_variable_functions.htm.md)**  

CML variable functions are fundamental tools used to perform both aggregation     (summarizing data from related components) and complex mathematical calculations on attribute     values (variables) within a configuration model. These functions are crucial for enforcing     dimensional validity and calculating derived attributes.

- 
**[Relationship Annotations](./cml_relationship_annotations.htm.md)**  

You can annotate relationships by using annotations, such as configurable,     allowNewInstance, closeRelation, sourceContextNode, and so on.
