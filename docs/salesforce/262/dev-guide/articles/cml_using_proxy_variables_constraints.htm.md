---
page_id: cml_using_proxy_variables_constraints.htm
title: Proxy Variables with Constraints on Types and Relationships
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_using_proxy_variables_constraints.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Proxy Variables with Constraints on Types and Relationships

Use proxy variables to reference the variables of related types, including parent,
root, and sibling types.

The supported proxy variables include:

- Cardinality
- Parent
- this.quantity

## Cardinality

Cardinality is a fundamental concept in Constraint Modeling Language (CML), controlling the
quantity of product instances allowed in a defined relationship. It is crucial for ensuring
product structure validity and optimizing performance.

The `cardinality` proxy variable refers to the
cardinality of a relationship, that is, the quantity of instances of the same type in a
relationship. The first parameter is the type name. The second, optional parameter is the
port name. This variable differs from the this.quantity proxy variable, which refers to the
quantity of the current instance.

Use this format:

```
cardinality(<type name>, <relation name>) or cardinality(<type name>)
```

Each parameter value can be a string or a string variable. If the relation name isn't
specified, the engine searches all ports to find the type.

The cardinality bounds are defined within the relation declaration using square brackets,
formatted as `[minimum..maximum]`.

## Cardinality Examples

These examples illustrate how cardinality is defined and managed in the Generator Set
model, focusing on standard definition, conditional enforcement, and reading the
quantity.

## Example 1: Using Cardinality Full Syntax

```
type Heater ;
type GeneratorSet  {
//Define the relation and specify the smallest cardinality required for performance
relation Heaters : Heater[0..10];
//Declare a variable to hold the count
int totalHeaterCount = [0..10];
// This counts instances of type "Heater" specifically within the "Heaters" relation.
int InstancesofHeater = cardinality(Heater, Heaters);
constraint(totalHeaterCount == InstancesofHeater);
// Optional message to display the count to the user
message(totalHeaterCount > 0, "Current configuration includes {} heaters.", totalHeaterCount, "Info");
}
```

See [Message
Rule](./cml_message_rule.htm.md "The message rule displays a message to users based on specified conditions.").

## Example 2: Using Cardinality Partial Syntax

```
type Heater ;
type OutputTerminal ;
// Main Generator Set type
type GeneratorSet {
// Define multiple relations that might contain specific types, each with a specified cardinality
relation Heaters : Heater[2];
relation OutputTerminals : OutputTerminal[0..99];
// Define derived attributes with an explicit domain
int totalHeatersFound = [0..100];
int totalTerminalsFound = [0..100];
// Partial cardinality SYNTAX
// The engine searches all relations to find the specified type
// Counts all instances of "Heater" across the entire GeneratorSet
int AllHeaterInstances = cardinality(Heater);
constraint(totalHeatersFound == AllHeaterInstances);
// Counts all instances of "OutputTerminal" across all relations
int AllOutputTerminals = cardinality(OutputTerminal);
constraint(totalTerminalsFound == AllOutputTerminals);
// Optional message for user visibility
message(totalHeatersFound > 0, "System found {} heaters in this configuration.", totalHeatersFound, "Info");
}
```

## Example 3: Defining Cardinality in Relations

This example shows how the Generator Set uses different cardinality ranges to define fixed
requirements, optional components, and minimum quantities for necessary components.

```
type GeneratorSet {
// 1. Fixed Cardinality: Exactly one General Model (component) is required.
// means min=1 and max=1.
relation GeneralModels : GeneralModel [1..1];
// 2. Bounded Optional Cardinality: Between 0 and 5 Temperature Sensors are allowed.
// [0..5] means the component is optional but limited.
relation TemperatureSensors : TemperatureSensor[0..5];
// 3. Minimum Required Cardinality: At least 1 Test record is required, up to 99.
// [1..99] enforces inclusion.
relation Testing : Test[1..99];
}
type GeneralModel;
type TemperatureSensor;
type Test ;
```

Key Concepts:

- Syntax: Cardinality is specified immediately after the component type in the relation
  declaration.
- Best Practice: Specifying the smallest required range, such as [1..1] or [0..5], ensures
  the constraint engine tests fewer combinations, which prevents performance
  degradation.

## Example 4: Enforcing Conditional Cardinality via require()

Cardinality can be dynamically enforced based on attributes of the parent product using the
`require()` constraint keyword. For more information,
see [Require
Rule](./cml_require_rule.htm.md "The require rule requires certain components to be included in a relationship when specified conditions are met.").

```
type GeneratorSet {
int requiredKW = [101..10000];
string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];
// Relation for mandatory installation accessories
relation Accessories : Accessory[1..99];
relation Testing : Test[1..99];
// Conditional Requirement based on power level:
// If the required power is over 5000 kW, exactly 5 specific Accessory instances are required.
require(
requiredKW > 5000,
Accessories [Accessory] == 5,
"High capacity generators require exactly 5 specialized accessory kits."
);
// Conditional Requirement based on compliance standard:
// If UL 2200 is selected, exactly 2 Test records must be included.
require(
standardsAndCompliance == "Listing-UL 2200",
Testing [Test] == 2,
"UL 2200 listing mandates exactly two certification tests."
);
}
type Accessory;
type Test;
```

This pattern (`require(condition, relation[type] == N,
...)`) allows the CML model to enforce a precise fixed number of child components
when a quantity threshold or attribute condition is met on the parent.

## Cardinality vs. Count

The `cardinality()` keyword is a proxy variable used to
refer to the size of a relationship. The `count()`
keyword is an aggregate function that counts matching components or attribute conditions
within a relation. Both can be used to read quantities for validation or aggregation
rules.

## Example for Similarity

Both `cardinality()` and `count()` can be used to determine the total quantity of items in a relationship.
In this scenario, they return the same value because the `count()` condition covers all possible active instances.

```
type Accessory{
boolean isPresent = true;
}
type Bundle {
relation items : Accessory[0..10];
int totalByCount = [0..10];
// Similarity: Both can read the headcount of the relation
// Use the proxy variable to set an attribute
int totalByCardinality = cardinality(Accessory, items);
// Use count() aggregate function within a constraint
constraint(totalByCount == items.count(isPresent == true));
}
```

## Example for Difference

The core difference is that cardinality is a proxy variable representing the headcount or
size of the relation, whereas count is a function used to evaluate specific attribute
conditions or filters within those instances.

```
type Accessory {
int weight = [1..100];
boolean isEssential;
}
type Bundle {
relation items : Accessory[1..20];
// 1. Declare variables with explicit domains
int totalHeadcount = cardinality(Accessory,items);
int heavyItemsCount = [0..20];
int essentialItemsCount = [0..20];
// DIFFERENCE 1: Cardinality (Proxy Variable)
// Cardinality refers to the relationship size (how many instances are present).
// It does not look at the values of the attributes within the instances.
// DIFFERENCE 2: Count (Aggregate Function)
// Count MUST use a logical expression to evaluate conditions within the relation.
// It filters the instances based on attribute logic before returning a total.
// Example: Counting only accessories that weigh more than 50kg
constraint(heavyItemsCount == items.count(weight > 50));
// Example: Counting only accessories marked as 'essential'
constraint(essentialItemsCount == items.count(isEssential == true));
// Business Logic using both:
message(
heavyItemsCount > (totalHeadcount / 2),
"Warning: More than half of your accessories ({}) are heavy items.",
heavyItemsCount
);
}
```

For more information, see [Message Rule](./cml_message_rule.htm.md "The message rule displays a message to users based on specified conditions.").

## Parent

The `parent()` proxy variable is used to enable
components at any level of the product hierarchy (child, grandchild, etc.) to access the
attributes (variables) defined by their ancestor types. This mechanism facilitates the flow
of configuration data and calculated values from the top of the bundle down to its
components.

The `parent()` keyword functions as a proxy variable
used to reference attributes residing in the immediate parent or any ancestor type in the
configuration model.

| Variable Name | Syntax | Purpose |
| --- | --- | --- |
| `parent()` | `parent(<ancestor variable name>, <level>)` | Retrieves the value of an attribute from a parent or ancestor type. |

## Key Characteristics

- Targeting Ancestors: The first parameter is the name of the attribute in the ancestor
  type that you wish to reference.
- Level Parameter: The second parameter (`<level>`) is optional and specifies how many levels up the hierarchy the
  engine should search. If omitted, it typically references the immediate parent. The level
  index for the `parent()` function effectively starts
  from 0 (implicit) for the immediate parent.
- Level 0 (Default): When you use `parent(attributeName)`, the engine references the attribute in the immediate
  parent.
- Level n: When you specify `parent(attributeName, 1)`,
  the engine reaches one level beyond the immediate parent, to the grandparent.
- Data Flow: `parent()` ensures that the data flows
  unidirectionally, where the child reads attributes calculated or defined by the parent,
  thereby helping to prevent complex circular dependencies.
- Single Inheritance: CML follows a single inheritance model, where a type can only extend
  one other type at a time.
- Same Variable Name: In CML, reusing the same variable name between a parent bundle and
  its child accessories is a standard architectural pattern for cascading values down a
  product hierarchy. This allows a child component to automatically inherit or synchronize
  its properties with the parent type, ensuring configuration consistency.

## Example: Standards and Compliance Synchronization

In this example, the `standardsAndCompliance` selection
made at the bundle level is automatically passed down to every accessory within that
bundle.

```
type AccessoryBundle {
// 1. Define the attribute at the Bundle level
string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];
// Relation to accessories
relation accessories : Accessory[1..10];
}
type Accessory {
// 2. Reuse the same variable name
// The parent() function targets the attribute in the immediate parent
string standardsAndCompliance = parent(standardsAndCompliance);
// Business Logic: If the inherited standard is UL 2200, price is affected
decimal(2) testingFee = [0.00..500.00];
constraint(standardsAndCompliance == "Listing-UL 2200" -> testingFee == 250.00);
}
```

The `parent()` proxy variable is essential for cascading
configuration data and constraints down the product hierarchy, allowing child components to
reference attributes defined by their ancestors.

## Example: Parent Attribute Reference

This example utilizes attributes found on the `GeneratorSet` type (the parent) and demonstrates how related components (like
TemperatureSensor) access those values using the parent() proxy variable. Here is the
hierarchy context.

| Parent Type | Relation Name | Child Type | Cardinality | Key Attribute Usage |
| --- | --- | --- | --- | --- |
| Root `GeneratorSet` | `TemperatureSensors` | `TemperatureSensor` | `[0..5]` | Defines primary inputs (`requiredKW`) and a derived attribute (`ULComplianceEnforced`) based on the `standardsAndCompliance` selection. |
| Child `TemperatureSensor` (Instance within `GeneratorSet` relation) | Not Applicable | Not Applicable | Not Applicable | Uses the `parent()` proxy variable to reference the `requiredKW` attribute from its ancestor (`GeneratorSet`). A constraint ensures the component's capacity (`maxOperatingKW`) meets the requirement inherited from the parent. |
| Grandchild `StatorTemperatureSensor` (Subtype of `TemperatureSensor`) | Not Applicable | Not Applicable | Not Applicable | Inherits functionality from `TemperatureSensor`. Uses parent() to retrieve the calculated `ULComplianceEnforced` boolean from the `GeneratorSet`. Enforces a conditional installation rule using the Implication Operator (->). |

```
// --- Parent Type (GeneratorSet) ---
type GeneratorSet {
// Attributes defined by the parent
int requiredKW = [101..10000]; // Required power rating
string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"]; // Compliance choice
// Derived status: True if UL 2200 is selected (precondition for compliance checks)
boolean ULComplianceEnforced = standardsAndCompliance == "Listing-UL 2200";
// Relation to child components
relation TemperatureSensors : TemperatureSensor[0..5];
}
// --- Child Component Type (TemperatureSensor) ---
type TemperatureSensor {
// Temperature sensors may have a model that defines max operating KW
int maxOperatingKW = [1000..10000];
// Retrieve the required KW value from the immediate parent (GeneratorSet)
int parentRequiredKW = parent(requiredKW);
// Constraint ensures the sensor can handle the power defined by the parent
constraint(maxOperatingKW >= parentRequiredKW, "Sensor capacity must meet the required KW set by the generator set.");
}
// --- Specific Sensor Type (Grandchild) ---
type StatorTemperatureSensor : TemperatureSensor {
// Retrieve the boolean compliance flag from the immediate parent (GeneratorSet)
boolean enforceULCompliance = parent(ULComplianceEnforced);
// Constraint ensures that if UL Compliance is enforced by the parent,
// this sensor must meet a specific installation requirement (e.g., must be shielded)
string installationMethod = ["Standard", "Shielded"];
constraint(enforceULCompliance -> installationMethod == "Shielded",
"UL Compliance requires a shielded temperature sensor installation."
);
}
// Note: To reference a value further up the hierarchy, the optional level parameter can be used:
// int grandParentValue = parent(requiredKW, 1); // Accesses attribute 1 level up
```

## Explanation of Parent Reference

- Direct Reference (Immediate Parent): In the `TemperatureSensor` type, `int parentRequiredKW =
  parent(requiredKW);` accesses the `requiredKW` attribute defined in the immediately superior type, which is
  `GeneratorSet`.
- Unidirectional Data Flow: The `parent()` proxy
  variable is critical for enabling unidirectional data flow, where calculated or defined
  values in the parent are read by children to enforce constraints. The engine ensures that
  parent aggregation and calculation are complete before the `parent()` function executes in the child component.

## this.quantity

`this.quantity` is a proxy variable used specifically to
access the quantity of the current instance (the specific product line item) within a
configuration.

## Key Characteristics and Usage

- Scope: It refers only to the quantity of the specific instance in which it is used. It
  is used at the component level to determine the quantity of that item chosen by the user
  or set by the constraint engine.
- Calculation Rule: The `this.quantity` proxy variable
  can be used only within a calculation rule.
- Distinction from `cardinality()`: `this.quantity` differs from the `cardinality()` proxy variable, which refers to the total number of instances of
  a specific type within a relationship and includes the quantity of other instances of the
  same type.
- Read-Only/Validation: When accessing quantity in CML, attributes like `this.quantity`, or external equivalents like `lineItemQuantity` or `ItemEndQuantity`, are treated as read-only and should be used only in
  calculation or evaluation rules. It is not recommended to use it to drive component
  creation, which should be done via cardinality.

## Example: Using this.quantity for Calculation

In the Generator Set configuration, a component like the `NaturalGasReformer` may use `this.quantity` to
define a local attribute representing how many units were selected, which is then used for
internal calculations (like total capacity or total weight contribution).

```
type LineItem;
type NaturalGasReformer : LineItem {
// 1. Definition: The LineItemQuantity attribute captures the quantity of this specific instance.
// The CML syntax dictates defining an attribute (LineItemQuantity) that equals this.quantity.
int LineItemQuantity = this.quantity;
// Placeholder: Attribute representing unit capacity per reformer unit
int unitCapacityKW = 100;
// 2. Calculation: Used in a calculation rule to determine total capacity based on the quantity selected for this line item instance.
int totalReformerCapacity = LineItemQuantity * unitCapacityKW;
}
```
