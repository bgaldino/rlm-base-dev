---
page_id: cml_global_properties_and_settings.htm
title: Global Properties and Settings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_global_properties_and_settings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_cml_core_concepts.htm
fetched_at: 2026-06-09
---

# Global Properties and Settings

Header-level declarations define the global properties and settings for a model, including
constants, properties, and external values that set up the foundation of the CML code.

Use these declarations to create reusable components and configuration settings that you can
reference throughout the model.

## Global Constants

Use global constants to define values that remain fixed throughout the model. These
constants can be numeric values, strings, lists, or other supported data types. Use
constants to create standardized settings or options that you can reference multiple times.
See [Example 1: Use Regex Global Variable](./cml_cml_core_concepts.htm.md "Constraint Modeling Language (CML) includes components that cover high-level global configurations to specific data types and constraints.").

In the example, `MAX_COUNT` is a global constant that is
hard-coded to `100: define MAX_COUNT 100`.

Regex (regular expressions) can be used to define global constants. The generalized
abstract syntax structure for regex expressions is define `<CONSTANT_NAME> "^<REGEX_PATTERN_STRING>$"`.

## Regex Pattern Components

This table lists regex components and their details.

| Regex Component | Description | Generalization |
| --- | --- | --- |
| ^ and $ | Anchors that ensure the pattern matches the entire string, from the beginning (^) to the end ($). | Ensures strict adherence to the required format. |
| () | Capturing Groups used to isolate portions of the matched string. You can reference the captured parts later by using $1, $2, and so on, in functions such as regexpreplace. See [String Variable Functions and Operators](./cml_string_variable_functions_and_operators.htm.md "Constraint Modeling Language (CML) provides string manipulation and conversion functions, and string comparison and validation operators."). | Allows extraction of specific data fields from a string. |
| + | Character Class and Quantifier that matches one or more (+) digits or characters. | Defines the permitted characters and minimum occurrences for the data fields. |
| / | Literal Character matching the forward slash separator present in the input data. | Matches fixed delimiters in the input string. |

In the example, `VOLTAGE_REGEX` is a global constant
that defines a fixed regular expression pattern used for validation or parsing throughout
the model define `VOLTAGE_REGEX
"^([0-9]+)/([0-9]+)$"`.

For more on the usage of global properties, see [External
Variables](./cml_external_variables.htm.md "External variables are global Constraint Modeling Language (CML) variables defined within a virtual CML type.").
