---
page_id: cml_annotation_example_sequence.htm
title: sequence Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_sequence.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_annotation_examples.htm
fetched_at: 2026-06-09
---

# sequence Annotation

The `sequence` annotation defines the execution and
configuration order of elements in a Constraint Modeling Language (CML) model.

`sequence` annotation specification: Variable and
Relationship

| Annotation | `sequence` |
| --- | --- |
| Applicable to | Variable and Relationship |
| Value Type/Values | integer Example: 1, 2, 10 |
| Description | If a sequence value is not explicitly defined, the configurator implicitly determines the order based on the variable or relationship declaration order in the CML model. If a sequence value is explicitly defined, the configurator uses the sequence number to control the order in which variables or relationships are configured. Variables or Relationships with lower sequence values are assigned first. |

## Example 1

In this example, the `sequence` annotation is not explicitly specified. The `defaultValue` is defined for 3 variables (`controlPlacement`, `commissioningScope`, and
`controlLanguage`) of the `Control` products. The model contains a
constraint.

```
type GeneratorSet {
    relation controls : Control[1..999999];
}

type Control {
	@(defaultValue = "Left")
	string controlPlacement = ["Left", "Right", "Top"];

	@(defaultValue = "None")
	string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

	@(defaultValue = "English")
	string controlLanguage = ["English", "Danish", "French"];

	constraint(controlPlacement == "Left" && controlLanguage == "English" -> commissioningScope == "Remote Support");
}
```

## Example Description and Configurator Result

The model defines 3 variables with `defaultValue`
annotation.

```
controlPlacement = "Left"
commissioningScope = "None"
controlLanguage = "English"
```

Even when sequence is not explicitly specified for the variables, the engine assigns it implicitly based on the variable declaration order in the CML type. For this example, the sequence for the variables is:

```
controlPlacement: sequence = 1 (highest priority)
commissioningScope: sequence = 2
controlLanguage: sequence = 3 (lowest priority)
```

The constraint specifies that a type with `controlPlacement ==
"Left"` and `controlLanguage ==
"English"` will have a `commissioningScope ==
"Remote Support":`.

```
constraint(controlPlacement == "Left" && controlLanguage == "English" -> commissioningScope == "Remote Support");
```

For any constraint, the engine enforces logical equivalence between the left-hand side
(before ->) and the right-hand side (after ->): if the left side evaluates to true,
the right side must also be true (and vice versa).

In this example, the engine resolves the true -> false constraint (to be false -> false): it modifies the controlLanguage with the highest sequence.

As a result, the Product Configurator will have next values for the variables:

```
controlPlacement = "Left"
commissioningScope = "None"
controlLanguage = "Danish"
```

## Example 2

In this example, the `sequence` annotation is explicitly specified and the defaultValue is defined for
3 variables (`controlPlacement`, `controlLanguage`, `commissioningScope`) of the `Control`
products. The model contains a
constraint.

```
type GeneratorSet {
    relation controls : Control[1..999999];
}

type Control{

@(defaultValue = "Left", sequence = 1)
string controlPlacement = ["Left", "Right", "Top"];

@(defaultValue = "English", sequence = 3)
string controlLanguage = ["English", "Danish", "French"];

@(defaultValue = "None", sequence = 2)
string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

constraint(controlPlacement == "Left" && controlLanguage == "English" -> commissioningScope == "Remote Support");
}
```

## Example Description and Configurator Result

This example is similar to Example 1, but the `sequence`
annotation is specified explicitly for the variables to control solver priority:

```
controlPlacement: sequence = 1 (highest priority)
controlLanguage: sequence = 3 (lowest priority)
commissioningScope: sequence = 2
```

The constraint specifies that a type with `controlPlacement ==
"Left"` and `controlLanguage ==
"English"` will have a `commissioningScope ==
"Remote Support":`.

```
constraint(controlPlacement == "Left" && controlLanguage == "English" -> commissioningScope == "Remote Support");
```

- Following the same logical equivalence for constraints described in Example 1 and considering
  the default values specified in the Example 2, the left side of the constraint is true
  (`controlPlacement = "Left"` and `controlLanguage = "English"`), while the right
  side is false (`commissioningScope =
  "None"`).
- Because the `commissioningScope` has higher priority than the
  `controlLanguage`, the engine avoids changing the
  `commissioningScope` and instead resolves the
  constraint by making the left side false.
- The `controlPlacement` has the highest priority sequence than
  the `controlLanguage`, so the engine modifies the
  controlLanguage as the most efficient way to satisfy the constraint.

Available values for the `controlLanguage: ["English",
"Danish", "French"]`. To make the left side of the constraint
false, the engine selects the first non-matching value (specified in CML domain): `"Danish"`.

As a result, the Product Configurator will have next values for the variables.

```
controlPlacement = "Left"
controlLanguage = "Danish"
commissioningScope = "None"
```

## Example 3

In this example, the `sequence` annotation is explicitly specified and the defaultValue is defined for
3 variables (`controlPlacement`, `controlLanguage`, and `commissioningScope`) of the `Control`
products. The model contains a
constraint.

```
type GeneratorSet {
    relation controls : Control[1..999999];
}

type Control{
    
@(defaultValue = "Left", sequence = 1)
string controlPlacement = ["Left", "Right", "Top"];

@(defaultValue = "English", sequence = 2)
string controlLanguage = ["English", "Danish", "French"];

@(defaultValue = "None", sequence = 3)
string commissioningScope = ["None", "Remote Support", "On-site Commissioning"];

constraint(controlPlacement == "Left" && controlLanguage == "English" -> commissioningScope == "Remote Support");
}
```

## Example Description and Configurator Result

This example is similar to Example 2, but the lowest priority sequence is specified for the
`commissioningScope`. This is a trigger for the engine
to modify the `commissioningScope` first to resolve the
true -> false constraint to be true -> true).

As a result, the Product Configurator will have next values for the variables:

```
controlPlacement = "Left"
controlLanguage = "English"
commissioningScope = "Remote Support"
```

## Example 4

In this example, the sequence annotation is not explicitly
specified for 3 relations (`voltageConnections`, `controls`, and `alternators`). The model contains a
constraint.

```
type GeneratorSet {
    relation voltageConnections : VoltageConnection[0..999999];
    relation controls : Control[1..999999];
    relation alternators : Alternator[1..999999];

    int alternatorsQty = controls[Control] + voltageConnections[VoltageConnection];
    constraint(alternators[Alternator] > 0 -> alternators[Alternator] == alternatorsQty, "alternators[Alternator] = controls[Control] + voltageConnections[VoltageConnection]");
}

type Alternator;

type VoltageConnection;

type Control;
```

## Example Description and Configurator Result

Even when sequence is not explicitly specified for the relations, the engine sets it implicitly based on the relation declaration order in the CML type. For this example, the sequence for the relations is:

```
relation voltageConnections: sequence = 1 (highest priority)
relation controls: sequence = 2
relation alternators: sequence = 3 (lowest priority)
```

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Use mindful sequencing in CML for variables and relations to avoid
backtracking issues. Define them in the order you expect the engine to modify them during
constraint resolution.

In this example, the CML model works without conflicts because the relations are implicitly
defined with the correct sequence. The `voltageConnections` and controls relations are evaluated first, then the `alternatorsQty` is calculated from their quantities. Finally,
the `alternators` relation is adjusted based on that
result. Because the `alternators` is processed last, the
engine avoids backtracking and errors.

## Example 5

In this example, the `sequence` annotation is explicitly specified for 3 relations (`voltageConnections`, `controls`, and `alternators`). The model
contains a constraint.

```
type GeneratorSet {
	@(sequence=3)
    relation alternators : Alternator[1..999999];
    @(sequence=1)
    relation voltageConnections : VoltageConnection[0..999999];
	@(sequence=2)
    relation controls : Control[1..999999];

    int alternatorsQty = controls[Control] + voltageConnections[VoltageConnection];
    constraint(alternators[Alternator] > 0 -> alternators[Alternator] == alternatorsQty, "alternators[Alternator] = controls[Control] + voltageConnections[VoltageConnection]");
}
type Alternator;

type VoltageConnection;

type Control;
```

## Example Description and Configurator Result

This example is similar to Example 4, but the `sequence`
is explicitly specified for the relations to control the processing priority and ensure the
engine evaluates and modifies them in the correct order during configuration.

## sequence Configuration Settings

Table 1. sequence Configuration Settings

| Associated Example | Product Group Structure | Applicable to | "sequence" annotation | User Action | Engine Action | UI Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| Example 1 | N/A | Variable | not specified | Configure the product containing variables | Assign the sequence for the variables based on the variable declaration order in the type. Enforce logical equivalence between left-hand side and right-hand side for the constraint by modifying the variable with the highest sequence | Display appropriate variable values based on sequence and constraint logic |
| Example 2  Example 3 | N/A | Variable | specified | Configure the product containing variables | Assign the sequence for the variables based on defined sequence annotation. Enforce logical equivalence between left-hand side and right-hand side for the constraint by modifying the variable with the highest sequence | Display appropriate variable values based on sequence and constraint logic |
| Example 4 | Individual product | Relationship | not specified | Configure the bundle product containing relationship products | Assign the sequence for the relationships based on the relation declaration order in the type. Execute the constraint (according to assigned sequence) | Display adjusted relationships based on the relationship sequence and constraint logic |
| Example 5 | Individual Product | Relationship | specified | Configure the bundle product containing relationship products | Assign the sequence for the relationships based on defined sequence annotation. Execute the constraint (according to specified sequence) | Display adjusted relationships based on the relationship sequence and constraint logic |
| N/A | Product Classification | Relationship | not specified | Configure the bundle product containing relationship products | Assign the sequence for the relationships based on the relation declaration order in the type. Execute the constraint (according to assigned sequence) | Display adjusted relationships based on the relationship sequence and constraint logic |
| N/A | Product Classification | Relationship | specified | Configure the bundle product containing relationship products | Assign the sequence for the relationships based on defined sequence annotation. Execute the constraint (according to specified sequence) | Display adjusted relationships based on the relationship sequence and constraint logic |
