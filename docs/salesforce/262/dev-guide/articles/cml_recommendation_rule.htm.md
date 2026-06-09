---
page_id: cml_recommendation_rule.htm
title: Recommendation Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_recommendation_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Recommendation Rule

The recommend keyword is used within a Constraint Modeling Language (CML) rule to
display suggestions for related products in the Product Configurator. The rule defines the
condition under which a specific product type or relation should be suggested to the
user.

You can recommend a type, a relation, or both in the same rule. The recommendation rule can be added inside a standalone product, a product bundle, or a virtual container.

Unlike action rules that are interpreted directly by the Product Configurator API, when the
condition is met, the engine forces a UI change (hiding or disabling a product option,
attribute, or value). Recommendations are not automatically applied to the UI by the
configuration engine alone. To suggest types or relations (products/bundles), typically for
up-selling or cross-selling based on their current selections at runtime, use the Run Config
Rules action within a Salesforce Flow. See [Run Config Rules Action](https://developer.salesforce.com/docs/./actions_obj_run_config_rules.htm.md "HTML (New Window)") in
the Revenue Cloud Developer Guide.

- Use an action rule when a selection makes another option invalid or irrelevant. For example, if a user selects a basic warranty, you should "hide" or "disable" the premium support options to prevent a conflicting or impossible setup.
- Use a recommendation rule when you want to nudge the user toward a beneficial add-on. For example, if a user buys a high-end generator, you "recommend" a maintenance service contract. This does not block the user if they choose not to add it.

Here are 3 examples demonstrating how to implement product recommendation rules.

## Example 1: Recommending a Type (Based on Attribute Selection)

This rule is placed within the `GeneratorSet` type. If a
user selects an extremely high voltage, the configuration engine recommends a specialized
engineer component required for installation or commissioning.

```
type GeneratorSet {
// Attribute input
string Voltage = ["277/480", "7976/13800"];
// Relation to the component type being recommended
relation engineers : engineer[0..99];
// Recommend Engineer Specialist (type) for High Voltage
rule(
Voltage == "7976/13800", "recommend", "type", "EngineerSpecialist"
);
}
// Recommended type
type EngineerSpecialist ;
type engineer;
```

## Example 2: Recommending a Relation (Based on Component Quantity)

This rule recommends adding items to an existing relation (`Accessories`) if the user selects a high-end component (such as the most robust
enclosure, `Enclosure_SA3`).

```
type GeneratorSet  {
// Relations defined in the GeneratorSet
relation Enclosures : Enclosure;
relation Accessories : Accessory[1..99]; // The relation being recommended
// Recommend Accessories when maximum sound dB is chosen
rule(
Enclosures[Enclosure_SA3] == 1,
"recommend",
"relation",
"Accessories");
}
type Enclosure ;
type Enclosure_SA3 : Enclosure;
type Accessory ;
```

## Example 3: Recommending a Type (From a Virtual/System Container)

This rule is applied at the Quote or System level (using a `virtual` type) and recommends a system integration product if multiple generators
are being configured, reflecting the requirement that large projects often need central
control components.

```
@(virtual = true)
type Quote {
// Relation referencing all GeneratorSet instances on the quote
@(sourceContextNode = "SalesTransaction.SalesTransactionItem")
relation lineItems : GeneratorSet[0..10];
// Recommend Switchgear for multi-unit orders
rule(
lineItems[GeneratorSet] > 1,
"recommend",
"type",
"Switchgear"
);
}
type GeneratorSet;
type Switchgear;
```
