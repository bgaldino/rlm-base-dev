---
page_id: cml_hide_disable_rule.htm
title: Hide or Disable Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_hide_disable_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Hide or Disable Rule

The Hide or Disable Rule uses the rule() keyword to conditionally remove an element
from the selection menu (hide) or preserve it in the menu while preventing user selection
(disable).

This functionality can be applied.

- On a bundle, hide a component to remove it from the selection menu, or disable a component to preserve it in the menu but prevent users from selecting options for it.
- On an individual product, hide an attribute to remove it from the selection menu, or disable an attribute to preserve it in the menu but prevent users from selecting options for it.
- On an attribute, hide or disable an attribute value to preserve it in the menu but prevent users from selecting options for it. For attribute values, the hide and disable rules have the same behavior.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

In Visual Builder in Salesforce, for attribute values, only the hide rule is
enabled. When you apply the hide rule to an attribute value in Visual Builder, the value
appears in the menu but selections are disabled.

The hide and disable rules use this syntax, where `action` is replaced by either `hide` or
`disable`.

```
rule(logic expression, action, actionScope, actionTarget)
rule(logic expression, action, actionScope, actionTarget, actionClassification, actionValueTarget)
```

## Example: Hiding and Disabling Features

In the example in this section, rules rely on specific variables to define the scope and target of the action.

| Variable in Rule | Purpose | Example from Generator Set | Description |
| --- | --- | --- | --- |
| `logic expression` (Declaration) | Condition upon which the rule occurs. | `requiredKW <= 500` | The logical test that triggers the action. |
| `action` | Designates whether the rule is hide or disable. | `"hide", "disable"` | Determines if the element is removed from view or made unselectable. |
| `actionScope` | Designates whether the rule acts on an attribute or relation scope. | `"attribute", "relation`" | Specifies if the target is a variable property or a component relationship. |
| `actionTarget` | Designates the specific variable or relation that the rule acts on. | `"Voltage", "StarterMotors"` | The Constraint Modeling Language (CML) name of the attribute or relation. |
| `actionClassification` | Designates whether the rule acts on a type or a value. | `"type", "value"` | Used when targeting components within a relation (type) or specific options within an attribute domain (value). |
| `actionValueTarget` | Designates the specific type or value that the rule acts on. | `"7976/13800", "StarterMotor_Advanced"` | The specific string value or type name to hide or disable. |

```
// --- Component Definitions (For relations referenced below) ---
type LineItem;
type EngineModel : LineItem;
type StarterMotor : LineItem;
type OutputTerminal : LineItem;
type OutputTerminals2HoleLugNEMA : OutputTerminal; // Specific terminal type
type GeneratorSet : LineItem {
// Attributes subject to hide/disable rules
int requiredKW = [101..10000];
string Voltage = ["220/380", "240/416", "4160/7200", "7976/13800"]; // Voltage is the attribute being hidden/disabled
string specialApplication = ["None - Standard", "Motor Starting"]; // specialApplication attribute contains a value to hide
// Relations subject to hide/disable rules
relation StarterMotors : StarterMotor; // Relation target (component) to hide/disable
relation OutputTerminals : OutputTerminal[0..99]; // Relation being acted upon
// 1. Disable a Component (Type) in a Relation
// If requiredKW is too low (<= 500 kW), the advanced starter motor component is disabled (visible but unselectable).
rule(
requiredKW <= 500,
"disable",
"relation",
"StarterMotors",
"type",
"StarterMotor_Advanced"     );
// 2. Hide an Attribute
// If the Generator is configured for a special purpose (Motor Starting), hide the Voltage attribute entirely.
rule(
specialApplication == "Motor Starting",
"hide",
"attribute",
"Voltage"
);
// 3. Hide a Specific Attribute Value
// If the power requirement is low (< 2000 kW), hide the high voltage option (7976/13800) from the Voltage attribute domain.
rule(
requiredKW < 2000,
"hide",
"attribute",
"Voltage",
"value",
"7976/13800"
);
// 4. Disable a Component Type (Alternate Syntax using the component name)
// Disable the OutputTerminals2HoleLugNEMA component if the required KW is high.
rule(
requiredKW >= 5000,
"disable",
"relation",
"OutputTerminals",
"type",
"OutputTerminals2HoleLugNEMA"
);
}
type StarterMotor_Advanced : StarterMotor; // Subtype used in the rule
```
