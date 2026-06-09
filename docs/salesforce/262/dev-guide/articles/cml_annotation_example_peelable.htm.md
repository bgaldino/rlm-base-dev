---
page_id: cml_annotation_example_peelable.htm
title: peelable Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_peelable.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# peelable Annotation

The `peelable` annotation is used to create soft
selection values and allow the engine to modify these selections to satisfy a
constraint.

| Annotation | `peelable` |
| --- | --- |
| Applicable to | Variable |
| Value Type/Values | true, false |
| Description | Indicates whether the constraint engine can override the variable's value (whether set by default or user selection) to resolve a conflict.   - If `peelable` annotation is set to `true`, the engine treats the value as a "soft   selection." When a configuration conflict occurs, the engine attempts to   "peel" (unbind) this variable and retry the solution. If a valid   configuration is found, the engine automatically changes the value to satisfy   constraints rather than displaying an error message. - If `peelable` annotation is set to `false`, the engine treats the value as a   "hard selection." If the value causes a conflict with a constraint,   the engine will not attempt to change it automatically. Instead, it will stop   and display a conflict error message to the user, requiring manual intervention   to resolve the issue. |

## Example 1: peelable = true (Soft Selection)

In this scenario, the `ServiceLevel` defaults to `"Standard"`. Because it is marked `peelable = true`, the Constraint Engine treats this value as a
"soft pick." It is authorized to override this value automatically if a conflict
arises with another selection.

```
type CloudSubscription {
    
    // User adds 5TB of storage
    int storageTB = [1..3]; 

    /* 
     * peelable=true: The engine acts as a "negotiator." 
     * If a constraint needs to change this value, the engine is allowed 
     * to "peel" (remove) the user's selection and apply the required value.
     */
    @(defaultValue = "Standard", peelable = true)
    string ServiceLevel = ["Standard", "Premium"];

    // Constraint: 5TB or more requires Premium Service
    constraint(storageTB >= 5 -> ServiceLevel == "Premium", "High storage requires Premium service");
}
```

## Example 2: peelable = false (Hard Selection)

In this scenario, `peelable` is omitted (defaulting to
`false`) or explicitly set to `false`. The engine treats the value `"Standard"` as a "hard constraint" or a
firm user commitment. It is not authorized to change it automatically.

```
type CloudSubscription {
    
    // User adds 5TB of storage
    int storageTB = [1..3]; 

    /* 
     * peelable=false (Default): The engine acts as a "validator."
     * It respects the current value as a hard fact. 
     * It cannot change "Standard" to "Premium" on its own.
     */
    @(defaultValue = "Standard", peelable = false)
    string ServiceLevel = ["Standard", "Premium"];

    // Constraint: 5TB or more requires Premium Service
    constraint(storageTB >= 5 -> ServiceLevel == "Premium", "High storage requires Premium service");
}
```

## Example Description and Configurator Result

In example 1, the `ServiceLevel` attribute is specified
with the `peelable` annotation set to `true`. In example 2, the annotation is not specified, so the
system considers it as false by default. As a result, if the user updates the `storageTB` variable to 5, the system automatically changes the
`ServiceLevel` to `"Premium"` in example 1 according to constraint logic, effectively
"peeling" the default `"Standard"`
value to resolve the conflict. The system allows this override without displaying an error
message to the user. In example 2, the system does not allow the engine to override the
default `"Standard"` value automatically.
Consequently, the system displays a conflict error message, and the user must manually
update the `ServiceLevel` to `"Premium"` to satisfy the constraint.

## Example 3: System-Driven Soft Selection (configurable = false, peelable = true)

In this example, the `Voltage` is set to a high voltage
(" `2400/4160`") by default. The annotation
`configurable = false` prevents the user from manually
changing this value in the UI. However, `peelable = true`
is added to allow the constraint engine to override this default if a specific compliance
standard is selected.

```
type GeneratorSet {
    
    string standardsAndCompliance = ["None", "Listing-UL 2200"];

    /* 
     * configurable=false: The user cannot change this directly.
     * peelable=true: The engine is authorized to change the default 
     * to resolve conflicts with the standardsAndCompliance selection.
     */
    @(defaultValue = "2400/4160", configurable = false, peelable = true)
    string Voltage = ["220/380", "277/480", "2400/4160"];

    // Constraint: UL 2200 listing requires a specific low voltage (277/480)
    constraint(standardsAndCompliance == "Listing-UL 2200" -> Voltage == "277/480");
}
```

## Example Description and Configurator Result

In example 3, the `Voltage` is specified with
configurable set to `false`, preventing user interaction,
but peelable is set to `true`. Initially, the system sets
the voltage to "`2400/4160`". If the user
updates the `standardsAndCompliance` variable to
"`Listing-UL 2200`", the system detects a
conflict with the default voltage. Because the variable is peelable, the system
automatically "peels" the default "`2400/4160`" value and changes it to "`277/480`" to satisfy the constraint. The transition happens silently without
a conflict error, even though the user cannot manually edit the field.

## Example 4: System-Driven Hard Constraint (configurable = false, peelable = false)

In this example, the `EmissionsTier` is set to
"`Tier 3`" by default. It is marked `configurable = false` (system-controlled) and `peelable` is omitted (defaults to false), treating the default
value as a hard constraint.

```
type GeneratorSet {

    string Location = ["US", "International"];

    /*
     * configurable=false: The user cannot change this.
     * peelable=false (Default): The engine treats "Tier 3" as a hard fact.
     */
    @(defaultValue = "Tier 3", configurable = false)
    string EmissionsTier = ["Tier 3", "Tier 4 Final"];

    // Constraint: US Location requires Tier 4 Final
    constraint(Location == "US" -> EmissionsTier == "Tier 4 Final", "US requires Tier 4 Final emissions");
}
```

## Example Description and Configurator Result

In example 4, the `EmissionsTier` is specified with
configurable set to `false`, and `peelable` is not specified (defaulting to `false`). As a result, the system considers the default value
"`Tier 3`" as a hard constraint that cannot
be overridden. If the user updates the Location variable to "`US`", the constraint engine attempts to enforce
"`Tier 4 Final`" but finds it cannot
overwrite the fixed "`Tier 3`" value.
Consequently, the system displays a conflict error message stating "`US requires Tier 4 Final emissions`," and the
configuration enters an invalid state because the user cannot manually change the
EmissionsTier to resolve it.

## Example 5: Auto-Correcting User Input (`configurable = true`, `peelable = true`)

In this example, the ``EnclosureType`` is
user-selectable (``` configurable = true` ``) and defaults to
"Standard". It is marked with `peelable = true`. This allows the engine to
override even an explicit user selection if a subsequent choice makes the enclosure
invalid.

```
type GeneratorAccessories {
    /* 
     * configurable=true: User explicitly selects 'Standard'.
     * peelable=true: Grants permission to override the User's selection 
     * to resolve conflicts with the Environment.
     */
    @(defaultValue = "Standard", configurable = true, peelable = true)
    string EnclosureType = ["Standard", "Heated", "Reinforced"];

    string Environment = ["Indoor", "Arctic"];

    // Constraint: Arctic requires Heated Enclosure
    constraint(Environment == "Arctic" -> EnclosureType == "Heated");
}
```

## Example Description and Configurator Result

In example 5, the ``EnclosureType`` is specified with
``configurable`` set to ``true`` and ``peelable`` set to ``true``. Initially, the system allows the user to confirm the
selection of "`Standard`". If the user
subsequently updates the ``Environment`` variable to
"`Arctic`", the system detects that
"`Standard`" is invalid. Typically, the
engine protects user selections and would throw an error. However, because ``EnclosureType`` is peelable, the system treats the user's
choice as a "soft pick." It automatically "peels" the "`Standard`" selection and changes it to "`Heated`" to satisfy the logic. The user sees their
previous selection update automatically to match the new environment requirement, preventing
a "dead end" configuration state.

## Example 6: Upstream Correction (`sequence`, `peelable = true`)

In this example, the ``Voltage`` is configured early in
the process (Sequence 1) with a default value of "`Low`". It is marked with ``peelable =
true`` to allow downstream selections to override this initial setting.

```
type GeneratorSet {
    /* 
     * sequence=1: Evaluated first. Defaults to 'Low'.
     * peelable=true: Allows 'Application' (seq=2) to force a change to this value.
     */
    @(defaultValue = "Low", sequence = 1, peelable = true)
    string Voltage = ["Low", "Medium", "High"];

    /* 
     * sequence=2: Evaluated after Voltage is set.
     * The user picks 'DataCenter', which requires High Voltage.
     */
    @(sequence = 2)
    string Application = ["Residential", "DataCenter"];

    // Constraint: DataCenter application forces High Voltage
    constraint(Application == "DataCenter" -> Voltage == "High");
}
```

## Example Description and Configurator Result

In example 6, the ``Voltage`` attribute is specified
with ``sequence`` set to `1` and ``peelable`` set to ``true``. As a result, the system initially sets the value to
"`Low`" before evaluating the ``Application`` attribute. If the user updates the ``Application`` variable to "`DataCenter`" (which runs at sequence 2), the system detects a conflict
between the established "`Low`" voltage and the
constraint requirement for "`High`" voltage.
Because ``Voltage`` is peelable, the system automatically
"peels" the default "`Low`" value and
changes it to "`High`" to satisfy the
constraint. The transition happens silently without a conflict error, effectively allowing a
later user choice to correct an earlier default assumption.

## Example 7: Guided Fallback (‘strategy`, `peelable = true`)

In this example, the ``ServiceTier`` defaults to
"`Bronze`" (the lowest value). It is marked
with ``peelable = true`` and ``strategy = "descending`"`. If a constraint forces a change from the
default, the strategy directs the engine to try the highest possible valid values first.

```
type ServicePlan {
    /* 
     * defaultValue="Bronze": Start cheap.
     * peelable=true: Allow upgrade if needed.
     * strategy="descending": If peeled, try 'Platinum' next (Max value), 
     * instead of creeping up to 'Silver'.
     */
    @(defaultValue = "Bronze", strategy = "descending", peelable = true)
    string ServiceTier = ["Bronze", "Silver", "Gold", "Platinum"];

    int UserCount = [1..1000];

    // Constraint: > 100 users requires Premium tiers (Gold or Platinum)
    constraint(UserCount > 100 -> ServiceTier in ["Gold", "Platinum"]);
}
```

## Example Description and Configurator Result

In example 7, the ``ServiceTier`` is specified with
``strategy`` set to "`descending`" and ``peelable`` set to
``true``. Initially, the system sets the value to
"`Bronze`". If the user updates the ``UserCount`` variable to 150, the constraint requires ``ServiceTier`` to be either "`Gold`" or "`Platinum`". Because
the variable is peelable, the system removes the "`Bronze`" selection. Instead of testing the next closest value ("`Silver`"), the "`descending`" strategy instructs the engine to attempt resolution starting
from the top of the domain. Consequently, the system automatically selects "`Platinum`" (the highest valid option) rather than
"`Gold`". The user sees the plan upgrade
immediately to the highest tier without an error message.
