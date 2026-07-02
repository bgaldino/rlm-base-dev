---
page_id: cml_annotation_example_relatedAttributes.htm
title: relatedAttributes Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_relatedAttributes.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# relatedAttributes Annotation

`relatedAttributes` is a Constraint Modeling
Language (CML) annotation that resets the domain to the original one for
domainComputation.

`relatedAttributes` annotation specification:
Variable

| Annotation | `relatedAttributes` |
| --- | --- |
| Applicable to | Variable and Relationship |
| Value Type/Values | String |
| Description | For Variables  If `relatedAttributes` annotation is not specified, the engine updates the variable domain according to domainComputation and constraint logic.  If the `relatedAttributes` annotation is specified with one or multiple values (separated by comma), the variable domain is reset to the original domain.  For relationships  If `domainComputation` is not explicitly specified, the engine sets it implicitly as true for the relationship.  If the `domainComputation` is specified as `true`, the relationship domain is dynamically determined based on the configuration and constraint logic.  If the `domainComputation` is specified as `false`, the relationship domain is fixed. |

## Example 1

In this example, the `relatedAttributes` annotation is not specified for the variables (`controlLanguage`, `controlPlacement`, `commissioningScope`) of
the `Control` type. The `domainComputation` annotation is defined for the variables. The model contains
the constraints.

```
type GeneratorSet {
    relation controls : Control;
}

type Control {
    @(domainComputation = true, defaultValue = "English")
    string controlLanguage = ["English", "Danish", "French"];

    @(domainComputation = true, defaultValue = "Left")
    string controlPlacement = ["Left", "Right", "Top"];

    @(domainComputation = true, defaultValue = "None")
    string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

    constraint(controlPlacement == "Right" -> commissioningScope != "Remote Support");

    constraint(controlLanguage == "Danish" -> commissioningScope != "On-site Commissioning");
```

## Example Description and Configurator Result

In example 1, the variables of the `Control` type are
not specified with the `relatedAttributes` annotation,
but defined with the `domainComputation` annotation. As a
result, the system updates the variable domain based on the constraint logic.

If the `controlPlacement` is selected with the
"`Right`" value, the `commissioningScope` variable domain is updated to exclude the
"`Remote Support`" value;

If the `controlLanguage` is selected with the “`Danish`" value, the `commissioningScope` variable domain is updated to exclude the "`On-site Commissioning`" value.

## Example 2

In this example, the `relatedAttributes` annotation is specified for the variable with one value. The
`domainComputation` annotation is defined for the
variables. The model contains the
constraints.

```
type GeneratorSet {
    relation controls : Control;
}

type Control {
    @(domainComputation = true, defaultValue = "English")
    string controlLanguage = ["English", "Danish", "French"];

    @(domainComputation = true, defaultValue = "Left")
    string controlPlacement = ["Left", "Right", "Top"];

     @(domainComputation = true, defaultValue = "None", relatedAttributes = "controlPlacement")
    string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

    constraint(controlPlacement == "Right" -> commissioningScope != "Remote Support");

    constraint(controlLanguage == "Danish" -> commissioningScope != "On-site Commissioning");
}
```

## Example 3

In this example, the `relatedAttributes` annotation is specified for the variable with one value. The
`domainComputation` annotation is defined for the
variables. The model contains the
constraints.

```
type GeneratorSet {
    relation controls : Control;
}

type Control {
    @(domainComputation = true, defaultValue = "English")
    string controlLanguage = ["English", "Danish", "French"];

    @(domainComputation = true, defaultValue = "Left")
    string controlPlacement = ["Left", "Right", "Top"];

    @(domainComputation = true, defaultValue = "None", relatedAttributes = "controlLanguage")
    string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

    constraint(controlPlacement == "Right" -> commissioningScope != "Remote Support");

    constraint(controlLanguage == "Danish" -> commissioningScope != "On-site Commissioning");
}
```

## Example Description and Configurator Result

In Example 2, the `relatedAttributes` annotation is
defined with the "`controlPlacement`" value for
the `commissioningScope` variable. As a result, the
system controls the domain for the `commissioningScope`
differently depending on `controlPlacement` or `controlLanguage` variable selection.

If the `controlPlacement` is selected with the
"`Right`" value, the `commissioningScope` variable domain remains unchanged, because
the `controlPlacement` is listed in the `relatedAttributes` annotation.

If the controlLanguage is selected with the “`Danish`" value, the `commissioningScope`
variable domain is updated to exclude the "`On-site
Commissioning`" value according to the constraint, because the `controlLanguage` is not listed in the `relatedAttributes` annotation.

In example 3, the `relatedAttributes` annotation is
defined with the "`controlLanguage`" value for
the `commissioningScope` variable. As a result, the
system controls the domain for the `commissioningScope`
differently depending on `controlPlacement` or `controlLanguage` variable selection.

If the `controlPlacement` is selected with the
"`Right`" value, the `commissioningScope` variable domain is updated to exclude the
"`Remote` Support" value according to the
constraint, because the `controlPlacement` is not listed
in the `relatedAttributes` annotation.

If the `controlLanguage` is selected with the
"`Danish`" value, the `commissioningScope` variable domain remains unchanged, because
the `controlLanguage` is listed in the `relatedAttributes` annotation.

## Example 4

In this example, the `relatedAttributes` annotation is specified for the variable with several values
(separated by comma). The domainComputation annotation is defined for the variables. The
model contains the
constraints.

```
type GeneratorSet {
    relation controls : Control;
}

type Control {
    @(domainComputation = true, defaultValue = "English")
    string controlLanguage = ["English", "Danish", "French"];

    @(domainComputation = true, defaultValue = "Left")
    string controlPlacement = ["Left", "Right", "Top"];

    @(domainComputation = true, defaultValue = "None", relatedAttributes = "controlPlacement, controlLanguage")
    string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

    constraint(controlPlacement == "Right" -> commissioningScope != "Remote Support");

    constraint(controlLanguage == "Danish" -> commissioningScope != "On-site Commissioning");
}
```

## Example Description and Configurator Result

In example 4, the `relatedAttributes` annotation is
defined with the "`controlPlacement`" and
"`controlLanguage`" values for the
commissioningScope variable. As a result, the system remains the `commissioningScope` variable domain unchanged.

If the `controlPlacement` is selected with the
"`Right`" value, the `commissioningScope` variable domain remains unchanged, because
the `controlPlacement` is listed in the `relatedAttributes` annotation.

If the controlLanguage is selected with the "`Danish`" value, the `commissioningScope`
variable domain remains unchanged, because the `controlLanguage` is listed in the `relatedAttributes` annotation.

## Example 5

In this example, the `relatedAttributes` annotation is not specified for the relationship (`temperatureSensors`). The `domainComputation` annotation is defined for the relationship. The model contains
the constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    
    @(domainComputation = true)
    relation temperatureSensors : TemperatureSensor[0..1];

    constraint(dutyRating == "Continuous Power (COP)" -> temperatureSensors[BearingTemperatureSensor] == 0);

    constraint(dutyRating == "Data Center Continuous (DCC)" -> temperatureSensors[StatorTemperatureSensor] == 0);
}

type TemperatureSensor;

type BearingTemperatureSensor : TemperatureSensor;

type StatorTemperatureSensor : TemperatureSensor;
```

## Example Description and Configurator Result

In example 5, the `temperatureSensors` relation is not
specified with the `relatedAttributes` annotation, but
defined with the `domainComputation` as true. As a
result, the system updates the relationship domain based on the constraint logic.

If the `dutyRating` is selected with the "`Continuous Power (COP)`" value, the system re-computes
the relationship domain and excludes the `BearingTemperatureSensor` product to satisfy the constraint. The `StatorTemperatureSensor` product remains and can be selected
in scope of the `GeneratorSet` bundle product.

If the `dutyRating` is selected with the "`Data Center Continuous (DCC)`" value, the system
re-computes the relationship domain and excludes the `StatorTemperatureSensor` product to satisfy the constraint. The `BearingTemperatureSensor` product remains and can be selected
in scope of the `GeneratorSet` bundle product.

## Example 6

In this example, the `relatedAttributes` annotation is specified for the relationship (`temperatureSensors`). The `domainComputation` annotation is defined for the relationship. The model contains
the constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    
    @(domainComputation = true, relatedAttributes = 'dutyRating')
    relation temperatureSensors : TemperatureSensor[0..1];

    constraint(dutyRating == "Continuous Power (COP)" -> temperatureSensors[BearingTemperatureSensor] == 0);

    constraint(dutyRating == "Data Center Continuous (DCC)" -> temperatureSensors[StatorTemperatureSensor] == 0);
}

type TemperatureSensor;

type BearingTemperatureSensor : TemperatureSensor;

type StatorTemperatureSensor : TemperatureSensor;
```

## Example Description and Configurator Result

In example 6, the `temperatureSensors` relation is
specified with the `relatedAttributes` annotation
containing the `dutyRating` value, the `domainComputation` annotation is defined as `true`. As a result, the system remains the relationship domain
unchanged and executes the constraints.

If the `dutyRating` is selected with the "`Continuous Power (COP)`" value, the system displays both
`BearingTemperatureSensor` and `StatorTemperatureSensor` products in scope of the `GeneratorSet` bundle product. The `BearingTemperatureSensor` product cannot be selected based on the constraint.

If the `dutyRating` is selected with the “`Data Center Continuous (DCC)`" value, the system displays
both `BearingTemperatureSensor` and `StatorTemperatureSensor` products in scope of the `GeneratorSet` bundle product. The `StatorTemperatureSensor` product cannot be selected based on the constraint.

## relatedAttributes Configuration Settings

Table 1. relatedAttributes Configuration Settings

| Associated Example | Product Group Structure | Applicable to | "relatedAttributes" annotation | "domainComputation" annotation | User Action | Engine Action | UI Behavior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Example 1 | Individual product | Variable | not specified | TRUE | Change variable value specified in constraint condition | Update the variable (specified with domainComputation) domain based on domainComputation and constraint logic | Display updated variable domain |
| Example 2  Example 3 | Individual product | Variable | specified (with one variable) | TRUE | Change variable value specified in constraint condition and relatedAttributes | Reset variable (specified in relatedAttributes) domain to the original domain | Display original variable domain |
| Example 4 | Individual product | Variable | specified (with several variables) | TRUE | Change variable values specified in constraint conditions and relatedAttributes | Reset variable (specified in relatedAttributes) domain to the original domain | Display original variable domain |
| Example 5 | Individual product | Relationship | not specified | TRUE | Change variable value specified in constraint condition | Update the relationship (specified with domainComputation) domain based on domainComputation and constraint logic | Display updated relationship domain |
| Example 6 | Individual product | Relationship | specified | TRUE | Change variable value specified in constraint condition and relatedAttributes | Reset relationship domain to the original domain | Display original relationship domain (products).  If the product is allowed according to constraint: the product can be selected  If the product is not allowed according to constraint: selected product returns back to unselected state |
| N/A | Product Classification | Relationship | not specified | TRUE | • Change variable value specified in constraint condition > Add products on browse popup from product classification  • Add products on browse popup from product classification > Change variable value specified in constraint condition | Update the relationship (specified with domainComputation) domain based on domainComputation and constraint logic | Display updated relationship domain. If the variable is changed again by the User, the value is reverted to the initial value |
| N/A | Product Classification | Relationship | specified | TRUE | • Change variable value specified in constraint condition > Add products on browse popup from product classification  •Add products on browse popup from product classification > Change variable value specified in constraint condition | • If the variable of constraint condition is changed first: update the relationship (specified with domainComputation) domain based on constraint logic  • if products are added first from browse popup: remain the relationship domain unchanged | • If the variable of constraint condition is changed first: display updated relationship domain. If the variable is changed again by the user, the value is reverted to the initial value  • if products are added first from browse popup: display added products as selected. If constraint variable is changed again by the user, the value is reverted to the initial value |
