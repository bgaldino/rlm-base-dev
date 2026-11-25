---
page_id: cml-annotation-example-defaultvalue
title: defaultValue Annotation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-annotation-example-defaultvalue.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-annotation-examples
legacy_page_id: cml_annotation_example_defaultValue.htm
fetched_at: 2026-11-25
---

# defaultValue Annotation

The `defaultValue` annotation is used on a variable to define the value it should start with when configuration begins.

| Annotation | `defaultValue` |
| --- | --- |
| Applicable to | Variable |
| Value Type/Values | Literal |
| Description | The configurator uses the default value defined in PCM (Product Attribute Definition). If no PCM default is available, the configurator uses the first value in the variable domain as the initial value. If no default value is defined in PCM and a defaultValue is specified in CML, the configurator uses the value defined in CML as the initial value of the variable. When you create or update an attribute by calling Product Configurator API while a constraint model is active, include `AttributeName` in the payload and set it to the attribute’s developer name. The constraint engine matches that value to the CML variable name. If the payload omits `AttributeName`, the engine applies the default described in this topic instead of the submitted value. See [Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes](./cml-best-practice-attribute-name.md). |

## Example 1

In this example, neither PCM nor CML defines a default value for the Cable Entry variable.

```
type GeneratorSet {
    relation voltageConnections : VoltageConnection[1..999999];
}
type VoltageConnection {
    string cableEntry = ["Top Entry", "Bottom Entry", "Side Entry"];
}
```

## Example Description and Configurator Result

The configurator sets `"Top Entry"` as the initial value for `Cable Entry`, because it is the first value in the variable domain `["Top Entry", "Bottom Entry", "Side Entry"`.

## Example 2

In this example, PCM (Product Attribute Definition) defines `"Bottom Entry"` as the default value for `Cable Entry`, and no `defaultValue` annotation is defined for this variable in CML.

```
type GeneratorSet {
    relation voltageConnections : VoltageConnection[1..999999];
}
// This annotation is added automatically if PCM has a default before the product is added to CML. If the product already exists in CML, the annotation is added or updated only after running Sync.
@(defaultValue = "Bottom Entry") 
type VoltageConnection {
    string cableEntry = ["Top Entry", "Bottom Entry", "Side Entry"];
}
```

## Example Description and Configurator Result

The configurator sets the `"Bottom Entry"` as the initial value for the `Cable Entry` of the `VoltageConnection` child products.

As a best practice, define the default value in PCM and use the Sync function in CML to keep the model aligned whenever PCM settings are updated.

## Example 3

In this example, a `defaultValue` annotation with `"Side Entry"` is defined in CML, and no default value is defined in PCM for the `Cable Entry` variable.

```
type GeneratorSet {
    relation voltageConnections : VoltageConnection[1..999999];
}

type VoltageConnection {
    @(defaultValue = "Side Entry")
    string cableEntry = ["Top Entry", "Bottom Entry", "Side Entry"];
}
```

## Example Description and Configurator Result

The configurator sets the `"Side Entry"` annotation value as the initial value for Cable Entry.

**Note:**

We recommend that you define default values in PCM (Product Attribute Definition) whenever possible, as this approach promotes consistency across products and simplifies maintenance.

The defaultValue annotation in CML should be used only when a default value is not suitable to be defined in PCM due to specific modeling requirements.

When a default value is defined in PCM but the CML model has not been synced, the configurator still applies the PCM default. However, the value displayed in the CML model may become inconsistent with PCM.

To avoid such inconsistencies, it is recommended to run the Sync action in CML after updating default values in PCM, so that the CML model remains aligned with the latest PCM settings.

## defaultValue Configuration Settings

| Associated Example | Configurable Specified | Configurable Value | defaultValue Specified | Initial Value Behavior | Example UI Result |
| --- | --- | --- | --- | --- | --- |
| Example 1 | No | default = TRUE | No | Uses the first value in the domain | Automatically set to “Top Entry” |
| Example 2 | Yes | TRUE | No | Uses the first value in the domain | Automatically set to “Bottom Entry” |
| Example 3 | Yes | FALSE | No | No initial value is set | Field remains empty |
| N/A | Yes | TRUE | Yes | Uses the value defined in defaultValue | Automatically set to “Side Entry” |
| N/A | Yes | FALSE | Yes | Still uses the value defined in defaultValue | Automatically set to “Side Entry” |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-annotation-example-defaultvalue.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
