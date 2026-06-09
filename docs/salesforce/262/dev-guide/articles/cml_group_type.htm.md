---
page_id: cml_group_type.htm
title: Group Type
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_group_type.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_types.htm
fetched_at: 2026-06-09
---

# Group Type

In Constraint Modeling Language (CML), a Group Type is used to logically containerize
related components within a bundle configuration, primarily when product component groups are
imported from Product Catalog Management (PCM).

The Group Type uses specific annotations to control the total quantity of components
selected from that group, regardless of the individual component type.

Bundles and Group Types (also known as Product Component Groups or PCGs) represent different levels of a product hierarchy and serve distinct functional roles in configuration logic.

## Conceptual Hierarchy

- Bundles are high-level parent products that contain multiple child products sold together as a package. In CML, they are defined as "root types" that encapsulate the properties, relationships, and constraints for the entire entity.
- Group Types are structural containers within a bundle. They act as intermediate folders that organize related components imported from Product Catalog Management (PCM). Instances of these Group Types are declared as variables inside the root Bundle type.

## Role in Cardinality and Selection

- Bundles establish the primary relationship between a root product and its broad categories of components.
- Group Types are specifically designed to enforce cardinality rules for a collection of
  products. They use the `@(minInstanceQty)` and `@(maxInstanceQty)` annotations to control exactly how many
  instances can be selected from a specific set of options (for example, "select at
  least 1 but no more than 2 accessories"). While the selected component can have a
  high quantity, the Group Type restricts the number of unique instances chosen from that
  group.

## Syntactic Implementation

- Accessing Components: For standard bundles, you reference components directly via their
  relation name. For components within a Group Type, you must use dot notation starting with
  the group variable name defined in the root type (for example, `accessoryGroup.mouse.Wireless == true`).
- Constraint Limitations: You cannot write a constraint directly on a Group Type's attribute to apply it to all components within that group; constraints must reference the specific child components.
- Identification: Group Types are automatically identified by a Group suffix and the presence of instance cardinality annotations during the import from PCM.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

The following examples are partial. See the complete code in the final CML
code sample.

## Example 1: Defining Generator Set Group Types

We can define two group types for a Generator Set configuration: `CoreModelGroup` (mandatory selection of a primary generator
model) and `EnclosureGroup` (optional selection of a
specific enclosure type).

For the `CoreModelGroup`, setting `minInstanceQty` to 1 and `maxInstanceQty` to 1 means that at least 1 is required, and a maximum of 1 is
permitted.

```
@(minInstanceQty=1, maxInstanceQty=1)
type CoreModelGroup {
// Relation holds the actual Generator Model products
relation generalModel : GeneralModel[0..9999];
}
type GeneralModel : LineItem {
int powerKW;
}
```

For the `EnclosureGroup`, setting `minInstanceQty` to 0 and `maxInstanceQty` to 1 means that selecting an enclosure is optional, but if
selected, the user can add at most one instance of an enclosure component (such as
WeatherproofEnclosure).

```
@(minInstanceQty=0, maxInstanceQty=1)
type EnclosureGroup {
relation enclosure : Enclosure;
relation cabinetHeater : ControlCabinetHeater;
}
type Enclosure : LineItem;
type ControlCabinetHeater : LineItem;
```

## Example 2: Referencing Group Types in the Root Bundle

Once defined, instances of these group types are used as variables within the root type,
which represents the entire bundle. In this example, the `coreModelGroup` and `enclosureGroup` are
instances of the respective group types, defined within the root type `GeneratorSetBundle`.

```
type GeneratorSetBundle {
CoreModelGroup coreModelGroup;
EnclosureGroup enclosureGroup;
}
```

## Example 3: Writing Constraints on Group Components

To write constraints or rules that reference components inside a group, use dot notation starting with the group variable name defined in the root type.

This example shows how a constraint might be defined within the `GeneratorSetBundle` type to enforce business logic on components within the
groups.

```
// If the selected generator model has a powerKW greater than 1500,
// then a Control Cabinet Heater must be included in the Enclosure Group.
constraint(coreModelGroup.generalModel.powerKW > 1500 ->
enclosureGroup.cabinetHeater[ControlCabinetHeater] == 1);
// Require an Enclosure component if the set requires seismic certification.
require(seismicCertification == "IBC Seismic Certification",
enclosureGroup.enclosure[Enclosure],
"Enclosure required for seismic certification");
```

## Final CML Code Sample with Group Types

This structure defines the complete model, showing the component hierarchy and the relationship constraints.

| Parent Type | Relation Name | Child Type | Cardinality | Key Attribute Usage |
| --- | --- | --- | --- | --- |
| `GeneratorSetBundle` | `coreModelGroup` (Group Instance) | `CoreModelGroup` | Group Cardinality: 1 | The group type defined by `@minInstanceQty=1, maxInstanceQty=1`. This enforces that exactly one component choice must be made from the internal generalModel relation. |
| `GeneratorSetBundle` | `enclosureGroup` (Group Instance) | `EnclosureGroup` | Group Cardinality: [0..1] | The group type defined by `@minInstanceQty=0, maxInstanceQty=1`. This enforces that selecting components from this group is optional (min 0) and at most one total component instance can be selected (max 1). |

```
/**
* The Root Bundle: GeneratorSetBundle
* This type holds instances of the defined Group Types and the definition of seismic certification */
type GeneratorSetBundle {
string seismicCertification = ["IBC Seismic Certification", "OSHPD Seismic Certification"];
CoreModelGroup coreModelGroup;
EnclosureGroup enclosureGroup;
// Constraint 1: If the selected GeneralModel has a powerKW greater than 1500,
// then a Control Cabinet Heater must be included in the Enclosure Group.
constraint(coreModelGroup.generalModel.powerKW > 1500 ->
enclosureGroup.cabinetHeater[ControlCabinetHeater] == 1);
// Constraint 2: Require an Enclosure component if the set requires seismic certification.
require(seismicCertification == "IBC Seismic Certification",
enclosureGroup.enclosure[Enclosure],
"Enclosure required for seismic certification");
// Action Rule Example: Disable a specific enclosure type if the core model is low power (e.g., 900kW).
rule(coreModelGroup.generalModel.powerKW == 900, "disable", "relation",
"enclosureGroup.enclosure", "type", "ReinforcedEnclosure");
}
/**
* Group Type 1: Core Model Group (Mandatory, Single Select)
* Min/Max Instance Quantity controls the selection rules for components within this group.
*/
@(minInstanceQty=1, maxInstanceQty=1)
type CoreModelGroup {
// Relation holds the actual Generator Model products
relation generalModel : GeneralModel[0..9999];
}
/**
* Group Type 2: Enclosure and Accessories Group (Optional)
* minInstanceQty=0 means selection is optional. maxInstanceQty=1 limits the selection to a single enclosure or accessory component instance.
*/
@(minInstanceQty=0, maxInstanceQty=1)
type EnclosureGroup {
relation enclosure : Enclosure;
relation cabinetHeater : ControlCabinetHeater;
}
/**
* Component Types (Children)
*/
type GeneralModel {
int powerKW;
}
type Enclosure {
@(defaultValue = "false")
boolean Weatherproof;
}
type ReinforcedEnclosure : Enclosure; // Subtype of Enclosure
type ControlCabinetHeater;
```

## Key Considerations

When reviewing Group Types in the context of the Generator Set model, keep these architectural points in mind.

- Group Cardinality Enforcement: The annotations `@(minInstanceQty)` (minimum instance quantity) and `@(maxInstanceQty)` (maximum instance quantity) are defined on the Group Type
  itself (`ElectricalSafetyGroup`). These annotations
  control the overall cardinality for all the components contained within that group,
  regardless of the individual relation cardinality defined (for example `[0..1]`, `[1..2]`).
- Root Reference: The `GeneratorSetBundle` includes the
  groups as variables (`coreModelGroup` and `enclosureGroup`).
- Constraint Syntax for Group Components: Constraints access attributes or components
  inside the groups using dot notation starting with the group variable name (for example,
  `coreModelGroup.generalModel.powerKW`).
- Limitation on Group Attributes: You cannot write a constraint directly on a group's
  attribute and expect it to apply to all components within that group (for example, `constraint(enclosureGroup.color == "Black")`) is
  not a valid constraint).

- **[Define Constraints for Quote Groups, Ramps, and Ramp Segments](./cml_quote_group_ramp_segment_constraints.htm.md)**  
  Apply rules to quote groups, ramps, and ramp segments by using the SalesTransactionItemGroup context tag. Assign a groupby value to messages defined in Constraint Rules Engine to include the messages in custom grouping strategies.
