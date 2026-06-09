---
page_id: cml_annotation_example_domainComputation.htm
title: domainComputation Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_domainComputation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# domainComputation Annotation

`domainComputation` is a CML annotation that specifies
how the domain of a model element is determined, either by using a fixed domain or by
computing the domain dynamically during configuration.

`domainComputation` annotation specification: Variable
and Relationship

| Annotation | `domainComputation` |
| --- | --- |
| Applicable to | Variable and Relationship |
| Value Type/Values | true, false |
| Description | `If domainComputation annotation is not explicitly specified, the engine sets it implicitly as false for the variable, and true for a relationship` If the `domainComputation` annotation is specified as `true`, the variable or relationship domain is dynamically determined based on the configuration and constraint logic.  If the `domainComputation` annotation is specified as `false`, the variable domain is fixed. |

## Example 1

In this example, the `domainComputation` annotation is not specified for the variable (voltage) of the
`GeneratorSet` type. The model contains the
constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"]
    constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");
    constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440");
}
```

## Example 2

In this example, the `domainComputation` annotation is explicitly specified as false for the variable
(voltage) of the `GeneratorSet` type. The model contains
the constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    @(domainComputation = false)
    string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"];
    constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");
    constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440");
}
```

## Example Description and Configurator Result

In example 1, the `domainComputation` annotation is not
explicitly specified for the `voltage` variable, but the
system considers it as `false` by default. In example 2,
the `domainComputation` annotation is explicitly defined
as `false`. As a result, the system remains the variable
domain unchanged `(["220/380", "240/416",
"347/600", "255/440", "277/480", "2400/4160",
"7200/12470", "7621/13200", "7976/13800"])` and
executes the constraints:

If the `dutyRating` is selected with the `"Continuous Power (COP)"` value, the `voltage` is pre-populated with the next possible value from
the variable domain `("240/416")` to satisfy
the constraint.

If the `dutyRating` is selected with the `"Data Center Continuous (DCC)"` value, the `voltage` is pre-populated with the `"255/440"` value to satisfy the constraint.

## Example 3

In this example, the `domainComputation` annotation is explicitly specified as `true` for the variable (`voltage`) of the `GeneratorSet` type. The
model contains the
constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    @(domainComputation = true)
    string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"];
    constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");
    constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440");
}
```

## Example Description and Configurator Result

In example 3, the `domainComputation` annotation is
explicitly specified as `true` for the `voltage` variable. As a result, the system updates the
variable domain based on the constraint logic.

If the `dutyRating` is selected with the `"Continuous Power (COP)"` value, the voltage is
pre-populated with the next possible value from the variable domain `("240/416")` to satisfy the constraint. The variable
domain is updated to exclude the `"220/380"`
value.

If the `dutyRating` is selected with the `"Data Center Continuous (DCC)"` value, the `voltage` is pre-populated with the `"255/440"` value to satisfy the constraint. The variable domain is
updated to contain only the `"255/440"`
value.

## Example 4

In this example, the `domainComputation` annotation is not specified for the relationship
(temperatureSensors). The model contains the
constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    relation temperatureSensors : TemperatureSensor[0..1];
    constraint(dutyRating == "Continuous Power (COP)" -> temperatureSensors[BearingTemperatureSensor] == 0);
    constraint(dutyRating == "Data Center Continuous (DCC)" -> temperatureSensors[StatorTemperatureSensor] == 0);
}
type TemperatureSensor;
type BearingTemperatureSensor : TemperatureSensor;
type StatorTemperatureSensor : TemperatureSensor;
```

## Example 5

In this example, the `domainComputation` annotation is explicitly specified as `true` for the relationship (temperatureSensors). The model
contains the constraints.

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

In example 4, the `domainComputation` annotation is not
explicitly specified for the `temperatureSensors`
relationship, but the system considers it as `true` by
default. In example 5, the `domainComputation` annotation
is explicitly specified as `true` for the relationship.
As a result, the system updates the relationship domain based on the constraint logic.

- If the `dutyRating` is selected with the `"Continuous Power (COP)"` value, the system
  re-computes the relationship domain and excludes the `BearingTemperatureSensor` product to satisfy the constraint. The `StatorTemperatureSensor` product remains and can be selected
  in scope of the `GeneratorSet` bundle product;
- If the `dutyRating` is selected with the `"Data Center Continuous (DCC)"` value: the system
  re-computes the relationship domain and excludes the `StatorTemperatureSensor` product to satisfy the constraint. The `BearingTemperatureSensor` product remains and can be
  selected in scope of the `GeneratorSet` bundle
  product.

## Example 6

In this example, the `domainComputation` annotation is explicitly specified as `false` for the relationship (`temperatureSensors`). The model contains the
constraints.

```
type GeneratorSet {
    @(defaultValue = "Emergency Standby Power (ESP)")
    string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];
    @(domainComputation = false)
    relation temperatureSensors : TemperatureSensor[0..1];
    constraint(dutyRating == "Continuous Power (COP)" -> temperatureSensors[BearingTemperatureSensor] == 0);
    constraint(dutyRating == "Data Center Continuous (DCC)" -> temperatureSensors[StatorTemperatureSensor] == 0);
}
type TemperatureSensor;
type BearingTemperatureSensor : TemperatureSensor;
type StatorTemperatureSensor : TemperatureSensor;
```

## Example Description and Configurator Result

In example 6, the `domainComputation` annotation is
explicitly specified as `false` for the relationship. As
a result, the system remains the relationship domain unchanged and executes the
constraints:

If the `dutyRating` is selected with the `"Continuous Power (COP)"` value, the system displays
both `BearingTemperatureSensor` and `StatorTemperatureSensor` products in scope of the `GeneratorSet` bundle product. The `BearingTemperatureSensor` product cannot be selected based on the constraint.

If the `dutyRating` is selected with the `"Data Center Continuous (DCC)"` value, the system
displays both `BearingTemperatureSensor` and `StatorTemperatureSensor` products in scope of the GeneratorSet
bundle product. The `StatorTemperatureSensor` product
cannot be selected based on the constraint.

## domainComputation Configuration Settings

Table 1. defaultValue Configuration Settings

| Applicable to | "domainComputation" annotation | User Action | Actual UI Behavior | Actual Engine Behavior | Constraint Model |
| --- | --- | --- | --- | --- | --- |
| string voltage | not specified | Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • Initial value for the voltage = the value specified in the @defaultValue annotation ("220/380")  • The user can select a different voltage value (e.g. "240/416", "255/440" etc.). The system remains User selected voltage  • The user can save the configuration with both values: initial voltage or user-selected voltage  Case 2: Duty Rating = "Continuous Power (COP)"  • Initial value for the voltage = next possible value from the domain to satisfy the constraint ("240/416")  • Warning: If the user selects a different voltage (e.g. "220/380", "255/440", "2400/4160" etc.), the system reverts it to the initial value ("240/416")  • The user can save the configuration with the initial voltage value (the configuration cannot be saved with other voltage due to reverting)  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • Initial value for the voltage = specified value in constraint that comes first in the domain ("220/380")  • The user can select a different vaild voltage specified in constraint ("255/440"). The system remains User selected voltage  • If the user selects a voltage that not vaild in the constraint (e.g. "240/416", "2400/4160" etc.), the system will revert it to one of the values defined in constraint ("220/380" or "255/440")  • The user can save the configuration with the specified in constraint voltage value (the configuration cannot be saved with other voltage due to reverting) | Always show the full voltage domain regardless of the Duty Rating selection. | Remain the full voltage domain.  Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • If the configuration is saved with initial (default) voltage value ("220/380"): attributeName":"voltage","cfgStatus":"Default"  • If the configuration is saved with User selected voltage value (e.g. "255/440"): attributeName":"voltage","cfgStatus":"Default"  Case 2: Duty Rating = "Continuous Power (COP)"  • If the configuration is saved with initial/reverted to initial voltage value ("240/416"): "attributeName":"voltage","cfgStatus":"Engine"  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • If the configuration is saved with initial ("220/380")/other constraint specified("255/440")/reverted to constraint specified voltage values ("220/380", "255/440"): "attributeName":"voltage","cfgStatus":"Default" | ``` type GeneratorSet {     @(defaultValue = "Emergency Standby Power (ESP)")     string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];      @(defaultValue = "220/380")     string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"];      constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");      constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440" || voltage == "220/380"); } ``` |
| string voltage | TRUE | Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • Display the full voltage domain  • Initial value for the voltage = the value specified in the @defaultValue annotation ("220/380")  • The user can select a different voltage value (e.g. "240/416", "255/440" etc.). The system remains User selected voltage  • The user can save the configuration with both values: initial voltage or User selected voltage  Case 2: Duty Rating = "Continuous Power (COP)"  • Display updated voltage domain according to the constraint (the "220/380" is not shown)  • Initial value for the voltage = next possible value from the domain to satisfy the constraint ("240/416")  • Warning: If the user selects a different voltage (e.g. "255/440", "2400/4160" etc.), the system reverts it to the initial value ("240/416")  • The user can save the configuration with the initial ("240/416") voltage value (the configuration cannot be saved with other voltage due to reverting)  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • Display updated voltage domain according to the constraint (only "220/380" and "255/440" are shown, other values are excluded)  • Initial value for the voltage = specified value in constraint that comes first in the domain ("220/380")  • Warning: If the user selects a different voltage specified in constraint ("255/440"), the system reverts it to the initial value ("220/380")  • The user can save the configuration with the initial voltage value (the configuration cannot be saved with the "255/440" voltage due to reverting) | Show updated voltage domain based on Duty Rating selection and constraint logic. | Update voltage domain based on Duty Rating selection and constraint logic.  Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • Remain the full voltage domain  • If the configuration is saved with initial (default) voltage value ("220/380"): attributeName":"voltage","cfgStatus":"Default"  • If the configuration is saved with User selected voltage value (e.g. "255/440"): attributeName":"voltage","cfgStatus":"Default"  Case 2: Duty Rating = "Continuous Power (COP)"  • Update voltage domain according to the constraint (exclude the "220/380" value)  • If the configuration is saved with initial/reverted voltage value ("240/416"): "attributeName":"voltage","cfgStatus":"Engine"  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • If the configuration is saved with initial ("220/380")/reverted to "220/380" constraint specified voltage value: "attributeName":"voltage","cfgStatus":"Engine" | ``` type GeneratorSet {     @(defaultValue = "Emergency Standby Power (ESP)")     string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];      @(defaultValue = "220/380", domainComputation = true)     string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"];      constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");      constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440" || voltage == "220/380"); } ``` |
| string voltage | FALSE | Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • Initial value for the voltage = the value specified in the @defaultValue annotation ("220/380")  • The user can select a different voltage value (e.g. "240/416", "255/440" etc.). The system remains User selected voltage  • The user can save the configuration with both values: initial voltage or User selected voltage  Case 2: Duty Rating = "Continuous Power (COP)"  • Initial value for the voltage = next possible value from the domain to satisfy the constraint ("240/416")  • Warning: If the user selects a different voltage (e.g. "220/380", "255/440", "2400/4160" etc.), the system reverts it to the initial value ("240/416")  • The user can save the configuration with the initial voltage value (the configuration cannot be saved with other voltage due to reverting)  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • Initialvalue for the voltage = specified value in constraint that comes first in the domain ("220/380")  • The user can select a different voltage specified in constraint ("255/440"). The system remains User selected voltage  • If the user selects a voltage that not specified in the constraint (e.g. "240/416", "2400/4160" etc.), the system will revert it to one of the values defined in constraint ("220/380" or "255/440")  • The user can save the configuration with the specified in constraint voltage value (the configuration cannot be saved with other voltage due to reverting) | Same as not specified  Always show the full voltage domain regardless of the Duty Rating selection. | Same as not specified  Remain the full voltage domain.  Case 1: Duty Rating = any except specified in constraints (e.g. "Prime Power (PRP)", "Emergency Standby Power (ESP)"):  • If the configuration is saved with initial (default) voltage value ("220/380"): attributeName":"voltage","cfgStatus":"Default"  • If the configuration is saved with User selected voltage value (e.g. "255/440"): attributeName":"voltage","cfgStatus":"Default"  Case 2: Duty Rating = "Continuous Power (COP)"  • If the configuration is saved with initial/reverted to initial voltage value ("240/416"): "attributeName":"voltage","cfgStatus":"Engine"  Case 3: Duty Rating = "Data Center Continuous (DCC)"  • If the configuration is saved with initial ("220/380")/other constraint specified("255/440")/reverted to constraint specified voltage values ("220/380", "255/440"): "attributeName":"voltage","cfgStatus":"Default" | ``` type GeneratorSet {     @(defaultValue = "Emergency Standby Power (ESP)")     string dutyRating = ["Emergency Standby Power (ESP)", "Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)"];      @(defaultValue = "220/380", domainComputation = false)     string voltage = ["220/380", "240/416", "347/600", "255/440", "277/480", "2400/4160", "7200/12470", "7621/13200", "7976/13800"];      constraint(dutyRating == "Continuous Power (COP)" -> voltage != "220/380");      constraint(dutyRating == "Data Center Continuous (DCC)" -> voltage == "255/440" || voltage == "220/380"); } ``` |
