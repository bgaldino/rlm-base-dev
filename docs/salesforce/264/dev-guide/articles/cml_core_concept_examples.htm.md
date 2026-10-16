---
page_id: cml_core_concept_examples.htm
title: Core Concept Examples
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_core_concept_examples.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Core Concept Examples

These examples illustrate core Constraint Modeling Language (CML) concepts including
    type, relationships, constraints, and so on.

    

For an explanation of the constraint model structure in these examples, see [Model
          Structure](./cml_appendix_model_structure.htm.md).

    

## Example 1: Use Regex Global Variable

      
      

```
// Global Constant: Regex used to parse voltage strings
define VOLTAGE_REGEX "^([11-19]+)/([11-19]+)$" 

type LineItem;
type GeneratorSet : LineItem {
   // Core attributes
   @(configurable = false)
   int requiredKW = [101..10000]; // Required power capacity
   string Voltage = ["220/380", "240/416", "277/480", "7976/13800"]; 
   string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];

   // Calculated attributes
   // Surge load is 1.25 times the required KW
   decimal(2) surgeLoadKW = requiredKW * 1.25; 
   // Voltage3 extracts the secondary voltage (e.g., 380 or 416) for checks
   int Voltage3 = strtoint(regexpreplace(Voltage, VOLTAGE_REGEX, "$2"), 0); 

   // Relation to model components 
   relation GeneralModels : GeneralModel[11]; 

   // Constraint 1: Ensure model capacity meets the required KW
   constraint(GeneralModels[GeneralModel].powerKW >= requiredKW, 
      "Selected Generator Model is insufficient for the required power."); 
   
   // Constraint 2: UL 2200 standard restricts voltage to 600V or less (Implication rule)
   constraint(standardsAndCompliance == "Listing-UL 2200" -> Voltage3 <= 600, 
      "The UL 2200 standard covers stationary engine generator assemblies rated at 600 volts or less.");
}

// Component type definition (GeneralModel is a product component)
type GeneralModel : LineItem {
   int powerKW = [900, 1200, 1500, 1750, 2500];
   int dB = [20..23];
}
```

    

    

## Key Technical Details

      
      

- The `GeneratorSet` type is related to the `GeneralModel` type through a single relation.

              
              
              
              
              
              
                
                  

                  

                  

                  

                  

                

              

              
                
                  

                  

                  

                  

                  

                

              

            
| Parent Type | Relation Name | Child Type | Cardinality | Key Attribute Usage |
| --- | --- | --- | --- | --- |
| `GeneratorSet` | `GeneralModels` | `GeneralModel` | Not Applicable | Constrained by `requiredKW` on the parent type. |

      

- Parent Type (`GeneratorSet`): Defined as a `LineItem` component, the `GeneratorSet` holds configuration parameters such as the user's power
          requirement (`requiredKW`), the specified voltage
            (`Voltage`), and compliance standards (`standardsAndCompliance`). It also includes calculated
          attributes like `surgeLoadKW` and `Voltage3`.

- Child Type (`GeneralModel`): Defined as a `LineItem` component, the `GeneralModel` specifies the technical attributes of the selected generator
          configuration, including its power output (`powerKW`)
          and noise rating (`dB`).

- Cardinality: The relation `GeneralModels : GeneralModel`
          specifies the quantity bounds for the component, indicating that exactly 11 instances of
          the `GeneralModel` type must be included in this
          configuration.

    

    

## Example 2: Use Groupby Annotation to Create Virtual Group

      
      

Using Groupby annotation for types, this model creates a virtual `VoltageGroup` for every unique voltage (for example,
        "220/380", "480/277") found in the transaction.

      

```
// 1. The physical product type
type GeneratorSet {
   @(configurable = false)
   int requiredKW = [101..10000];

   string Voltage = ["220/380", "240/416", "255/440", "277/480"];

   // Calculation with explicit domain for best practice
   decimal(2) surgeLoadKW = [126.25..12500.00];
   constraint(surgeLoadKW == requiredKW * 1.25);
}

// 2. The virtual container grouped by the "Voltage" attribute
@(split=true, virtual=true, groupBy=Voltage)
type VoltageGroup {
   string Voltage; // The attribute used for grouping
   decimal(2) groupTotalSurgeKW = [0.00..99999.99];

   // Map instances to this group from the transaction line items
   @(sourceContextNode="SalesTransaction.SalesTransactionItem")
   relation generators : GeneratorSet[0..50];

   // Aggregation: Sum only the surge load of generators in THIS voltage group
   constraint(groupTotalSurgeKW == generators.sum(surgeLoadKW));

   // Business Rule: Limit total surge load per voltage branch
   message(groupTotalSurgeKW > 10000, "Warning: Surge load for Voltage {} exceeds branch capacity!", Voltage);
}

// 3. The top-level system managing the groups
@(virtual = true)
type GeneratorSystem {
   relation generators : GeneratorSet[0..100];
   relation voltageGroups : VoltageGroup[1..10];

   decimal(2) systemTotalKW = voltageGroups.sum(groupTotalSurgeKW);
}
```

    

    

## Key Technical Details

      
      

- 
`groupBy=Voltage`: The engine scans all `GeneratorSet` instances and creates one virtual `VoltageGroup` for each unique voltage value detected (for
          example, one group for all "220/380" units, another for all "277/480"
          units).

- 
`sourceContextNode`: This tells the virtual group to pull its
          "children" (the generators) from the specific path in the Salesforce context
          where quote line items are stored.

- Bottom-Up Aggregation: Each `VoltageGroup` independently
          calculates its `groupTotalSurgeKW` based strictly on
          the generators assigned to it by the groupBy logic.

- Explicit Domains: Following best practices, the `surgeLoadKW`
          and `groupTotalSurgeKW` use explicit domains (for
          example, [0.00..99999.99]) to prevent "NullPointer" or initialization errors
          during solving.

    

    

## Example 3: Use Sharingcount Annotation to Reuse Accessory Instances

      
      

In this example, we apply sharingcount annotation to the `Accessory` type to allow the engine to reuse accessory instances across the
        configuration up to a specified limit.

      

```
// 1. Define the component type with split and sharingCount
// split=true enables parallel solving by splitting quantity into multiple instances
// sharingCount=5 allows a single Accessory instance to be reused 5 times in the model
@(split = true, sharingCount = 5)
type Accessory {
   string category;
   decimal(2) weight;
}

type GeneratorSet {
   @(configurable = false)
   int requiredKW = [101..10000];

   // 2. Define the relationship with the sharing annotation
   // @(sharing = true) allows the engine to satisfy this relation by 
   // "pointing" to existing instances instead of creating new ones 
   @(sharing = true)
   relation Accessories : Accessory[1..99];
}
```

    

    

## Key Technical Details

      
      

- Parallel Solving: By setting `split = true`, the engine can
          process the 99 possible accessories in parallel rather than sequentially, which is
          critical for large-scale generator configurations.

- Resource Management: The `sharingCount = 5` tells the solver
          that it doesn't need to instantiate 99 unique `Accessory` objects; it can reuse the same object definition up to five times
          across different parts of the configuration graph.

- Relationship Requirement: For `sharingCount` to take effect,
          the Relation (the port) must also be annotated with `@(sharing
            = true)` to grant the engine permission to reuse instances.

    

    

## Example 4: Use contextPath and tagName Annotations

      
      

```
// 1. GLOBAL EXTERN DECLARATIONS
// Unifying contextPath (header field) and tagName (context identifier)
@(contextPath = "SalesTransaction.ShippingCountry", tagName = "Region_Identifier")
extern string ShippingCountry = "International";

@(contextPath = "SalesTransaction.ProjectUrgency", tagName = "Priority_Level")
extern string ProjectUrgency = "Standard";

// 2. PHYSICAL PRODUCT TYPE
type GeneratorSet {
   // Core technical attributes
   @(configurable = false)
   int requiredKW = [101..10000];

   string DutyRating = ["Prime Power (PRP)", "Emergency Standby Power (ESP)"];
   
   // Technical calculation with explicit domain (Best Practice)
   decimal(2) surgeLoadKW = [126.25..12500.00]; 
   constraint(surgeLoadKW == requiredKW * 1.25);

   // 3. LOGIC INTEGRATING EXTERNAL DATA
   // Using contextPath/tagName data to drive technical warnings
   message(ShippingCountry == "US", 
           "Regional Notice: Generator must comply with US-specific UL 2200 standards.");

   message(ProjectUrgency == "Critical" && requiredKW > 5000, 
           "High Priority Alert: Large scale power requirement in a Critical project requires site inspection.", 
           requiredKW, "Warning"); 
}
```

    

    

## Key Technical Details

      
      

- External Variable (`extern`): These are declared outside of
          any type to hold values supplied by the environment (Salesforce).

- 
`contextPath` Annotation: This maps the variable directly to
          a header-level field in the Sales Transaction.

- 
`tagName` Annotation: This links the variable to a specific
          Context Tag identifier within the Salesforce Context Definition.

      

#### Note

Rules depending on these external variables (such as the `ShippingCountry` message) only re-evaluate when a Line Item
        change occurs (For example, updating `requiredKW`), not
        solely when the header field changes.

    

    

## Example 5: Use Format Specifiers (%s, %d) and Dates in Constraints

      
      

In this example, we define a generator configuration that validates the required power
          (`requiredKW`) against the duty rating and voltage,
        providing specific feedback when a mismatch occurs.

      

```
type GeneratorSet  {
   // 1. Core Technical Attributes with explicit domains
   @(configurable = true)
   int requiredKW = [101..10000];

   string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)",
                        "Data Center Continuous (DCC)", "Emergency Standby Power (ESP)"];

   string Voltage = ["220/380", "277/480", "347/600", "2400/4160"];

   string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];

   // Date Attribute Definition
   // Date variables represent a specific day.
   // You can define a fixed domain for a date as a range between two dates.
   date requestedDeliveryDate = ["2024-01-01".."2025-12-31"];

   // Message Rule with Multiple Arguments using placeholders
   message(requiredKW > 5000 && DutyRating == "Emergency Standby Power (ESP)",
           "High Capacity Alert: The %s rating for %d kW requires an additional cooling system.",
           DutyRating, requiredKW, "Warning");

   // Constraint with Multiple Arguments using placeholders
   constraint(Voltage == "2400/4160" && standardsAndCompliance == "Listing-UL 2200",
              "Configuration Error: Voltage %s cannot be used with %s standards due to safety limits.",
              Voltage, standardsAndCompliance);

   // Dates can be used in logical expressions with comparison operators like < or >=.
   message(requestedDeliveryDate < "2024-09-01" && requiredKW > 7000,
           "Schedule Warning: Delivery for %d kW units on %s may require expedited manufacturing.",
           requiredKW, requestedDeliveryDate, "Info");
}
```

    

    

## Key Technical Details

      
      

- Multiple Arguments: You can pass several variables after the string literal. The engine maps them to the placeholders in the exact order they appear.

- Format Specifiers

- 
`%s` is used for string variables (for example, `DutyRating` or `Voltage`).

- 
`%d` is used for integer variables (for example, `requiredKW`).

- Placeholder Usage: Alternatively, you can use the {} syntax, which the constraint engine automatically replaces with the actual argument values during runtime evaluation.

- Comparison Logic with Dates: You can treat dates as comparable values in `constraint` or `message`
          rules to enforce scheduling logic (for example, ensuring a delivery date is not too early
          for a complex build).

    

    

## Example 6: Use Arithmetic Calculations and Functions

      
      

This example demonstrates using aggregate functions (a virtual type for transaction-level
        aggregation) and mathematical functions within the `GeneratorSet` type for precise quantity calculation.

      

```
// --- Component Definition —
type GeneratorSet  {
    int requiredKW = [101..10000];
    int quantity = [1..10]; 
    // BEST PRACTICE: Define derived attributes with an explicit domain
    decimal(2) surgeLoadKW = [0.00..12500.00]; 
    // BEST PRACTICE: Put calculations inside of constraints
    constraint(surgeLoadKW == requiredKW * 1.25);
}
// --- Accessory Definition ---
type Accessory  {
    int weight_kg = [1..100];
}
// --- Virtual System Type (Aggregation Context) ---
@(virtual = true)
type System {
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
    relation generators : GeneratorSet[0..10];
	relation shipmentbatch : ShipmentBatch [0..10];
    // BEST PRACTICE: Attributes must have explicit domains
    decimal(2) totalQuotedLoad = [0.00..125000.00];
    int highPowerCount = [0..10];
    // Aggregate calculations in separate constraints
    constraint(totalQuotedLoad == generators.sum(surgeLoadKW));
    // VARIATION: Condition-based count
    // count() requires a logical expression 
    constraint(highPowerCount == generators.count(requiredKW > 5000));
    // Ensuring Shipment batch crates are similar to the number of generators
    message(
        shipmentbatch.requiredCrates != generators[GeneratorSet], 
        "The Shipment items ({}) must match the number of Generators ({})", 
        shipmentbatch.requiredCrates, generators[GeneratorSet], 
        "Error"
    );
}
type ShipmentBatch {
    int totalItems = [1..100];
    int itemsPerCrate = 10;
    // BEST PRACTICE: Define derived attributes for the relation in the parent type
    int totalWeight = [0..1000];
    int accessoryCount = [0..10];
    // Aggregates within the relation block
    relation accessories : Accessory[0..10] {
        accessoryWeight = sum(weight_kg); 
        accessoryCount = count(weight_kg > 0); 
    }
    // Mapping relation attributes to parent variables via constraints
    constraint(totalWeight == accessories.accessoryWeight);
    constraint(accessoryCount == accessories.accessoryCount);
    int requiredCrates = [0..100];
    // Mathematical Function Example: CEIL
    constraint calculateCeil(requiredCrates == ceil(totalItems / itemsPerCrate));
}
```

    

    

## Key Considerations for Calculations and Aggregations

      
      

When implementing these functions in CML, follow these architectural best practices for robustness and performance.

      

- Explicit domains are required: All the derived attributes that result from a calculation or aggregation must have an explicit variable domain definition. This practice ensures accurate aggregation and helps prevent runtime errors.

- Separate calculation from declaration: Define the aggregation or calculation in a separate
          constraint rather than using an inline derived attribute declaration (for example, `int total = items.sumPrice;`). This separation helps avoid
          issues where domains may not initialize correctly.

- Correct Pattern: Define the relation aggregate (`totalQty =
            sum(quantity);`) and then enforce the result via a constraint (`constraint(totalItemCount == items.totalQty);`).

    

    

## Example 7: Use Asset-Based Constraints Across Transaction and Installed Base

      
      

This example shows how to enforce quantity rules that span both in-flight items on the
        current sales transaction and products the customer already owns (the installed base). The
          `sourceContextNode="Asset"` annotation on a relation
        pulls existing asset records into the model as read-only data, so that a `require()` rule can combine those asset quantities with
        in-transaction quantities to drive configuration logic.

      

```
// 1. Top-level virtual type that organizes generator sets by fuel type
@(virtual=true)
type ServiceOrder {
  relation groups : GeneratorGroup;
}

// 2. Virtual group type: the engine creates one GeneratorGroup instance
// for each unique FuelType value found in the sales transaction
@(virtual=true, groupby=FuelType)
type GeneratorGroup {

  // In-flight generator sets on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation generators : GeneratorSet;
  constraint(generators[GeneratorSet] < 10, "Generator qty should be less than 10");
  constraint(generators[GeneratorSet].Discount > 10 && generators[GeneratorSet].Discount < 20,
             "Discount should be between 10 and 20");

  // In-flight heaters on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation heaters : Heater;

  // Existing heaters retrieved from the customer's installed base (Assets)
  // closerelation=true prevents the engine from adding new records to this relation
  @(sourceContextNode="Asset", closerelation=true)
  relation heaterAssets : Heater;

  // Asset-based require rule: when combined in-flight and installed heater
  // quantity exceeds 10, exactly 100 generator sets are required
  require(heaters[Heater] + heaterAssets[Heater] > 10, generators[GeneratorSet] == 100);
}

// 3. Physical product types
type GeneratorSet {
  string FuelType = ["Natural Gas", "Diesel", "Propane"];
  decimal Discount = [0..100];
}

type Heater {
  boolean AutoIgnition;
}
```

    

    

## Key Technical Details

      
      
        
- 
`sourceContextNode="SalesTransaction.SalesTransactionItem"`:
          Binds the relation to line items on the current quote or order. The engine reads and writes
          these instances during configuration.

        
- 
`sourceContextNode="Asset"`: Binds the relation to
          asset records that represent products the customer already owns from prior transactions.
          These records exist outside the current transaction and are treated as read-only context
          data.

        
- 
`closerelation=true`: Required on asset-sourced
          relations to prevent the engine from attempting to add new instances to the installed base.
          Without this annotation, the engine may try to create asset records to satisfy cardinality
          or require rules.

        
- Asset-based `require()`: The rule `require(heaters[Heater] + heaterAssets[Heater] > 10,
            generators[GeneratorSet] == 100)` combines cardinality from two separate
          relations — one sourced from the transaction and one from the installed base — in a single
          logical expression. This lets the model enforce quantity thresholds that account for what
          the customer is buying now and what they already have.

        
- Virtual grouping: The `groupby=FuelType` annotation
          on `GeneratorGroup` ensures that the asset-based
          constraint is evaluated independently per fuel type, so heaters and generator sets of
          different fuel types do not count toward each other's totals.

      

    

    

## Example 8: Use Asset Scope to Drive Auto-Add Logic

      
      

These examples show how to use the installed base (existing customer assets) as a condition
        in a `require()` rule to automatically add products to
        the current quote. The positive asset check triggers an auto-add when the customer already
        owns a product. The negative asset check enforces a prerequisite product when the customer
        does not yet own it.

      

Positive asset check: if the customer already owns at least one `GeneratorSet` in their installed base, the engine automatically adds a `MaintenanceKit` to the current quote.

      

```
@(virtual=true)
type ServiceOrder {
  // In-flight generator sets on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation generators : GeneratorSet;

  // Existing generator sets from the customer's installed base (read-only)
  @(sourceContextNode="Asset", closeRelation=true)
  relation generatorAssets : GeneratorSet;

  // In-flight maintenance kits on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation maintenanceKits : MaintenanceKit;

  // Positive asset check: customer already owns a GeneratorSet,
  // so automatically require a MaintenanceKit on the quote
  require(generatorAssets[GeneratorSet] >= 1, maintenanceKits[MaintenanceKit]);
}

type GeneratorSet;
type MaintenanceKit;
```

      

Negative asset check: if the customer does not yet own a `GeneratorSet` in their installed base but is adding more than one `MaintenanceKit` to the quote, the engine requires a `GeneratorSet` to also be added to the quote.

      

```
@(virtual=true)
type ServiceOrder {
  // In-flight generator sets on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation generators : GeneratorSet;

  // Existing generator sets from the customer's installed base (read-only)
  @(sourceContextNode="Asset", closeRelation=true)
  relation generatorAssets : GeneratorSet;

  // In-flight maintenance kits on the current sales transaction
  @(sourceContextNode="SalesTransaction.SalesTransactionItem")
  relation maintenanceKits : MaintenanceKit;

  // Negative asset check: customer does not own a GeneratorSet yet,
  // but is adding more than one MaintenanceKit, so require a GeneratorSet on the quote
  require(generatorAssets[GeneratorSet] < 1 && maintenanceKits[MaintenanceKit] > 1, generators[GeneratorSet]);
}

type GeneratorSet;
type MaintenanceKit;
```

    

    

## Key Technical Details

      
      
        
- Positive asset check (`generatorAssets[GeneratorSet] >=
            1`): Evaluates to true when the installed base contains at least one matching
          asset. Use this pattern to trigger upsell or companion-product logic for existing
          customers.

        
- Negative asset check (`generatorAssets[GeneratorSet] <
            1`): Evaluates to true when the customer has no matching asset. Use this pattern
          to enforce a prerequisite product for net-new buyers.

        
- Auto-add result: When the `require()` condition is
          met, the engine adds the specified product to the relation automatically. Passing only the
          relation and type without a quantity (`maintenanceKits[MaintenanceKit]`) requires exactly one instance. Append `== N` to require a specific quantity.

        
- 
`closeRelation=true` is required on the asset
          relation to prevent the engine from attempting to write back to the installed base when
          evaluating the condition.
