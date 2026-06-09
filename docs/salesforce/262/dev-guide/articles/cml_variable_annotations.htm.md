---
page_id: cml_variable_annotations.htm
title: Variable Annotations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_variable_annotations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_variables.htm
fetched_at: 2026-06-09
---

# Variable Annotations

You can annotate variables with properties such as configurable, defaultValue,
domainComputation, and relatedAttributes.

In this example, the `gc_runningKw` variable is
annotated to indicate that it's not configurable and has a default value of `0.00`.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This example requires an enclosing type.

```
@(configurable = false, defaultValue = 0.00)
decimal(2) gc_runningKw;
```

| Property | Values | Description |
| --- | --- | --- |
| allowOverride | true, false | Allows the engine to recalculate a value even if a value was already received from core.  This annotation helps save on performance by allowing early calculation. |
| configurable | true, false | Indicates whether the variable is configurable (`true`) or not (`false`).  If the configurable annotation isn’t explicitly specified, the engine sets it implicitly as `true` for the variable.  If the configurable annotation is explicitly specified as `true`, the variable is indicated as configurable. The engine can set the value to the variable according to the defined logic, and users can modify it.  If the configurable annotation is explicitly specified as `false`, the engine cannot set a value to the variable, and users can't update it. The variable value in this case is set through the PCM default.  See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| defaultValue | literal | Indicates the default value for the variable.  The configurator uses the default value defined in PCM (in Product Attribute Definition). If no PCM default is available, the configurator uses the first value in the variable domain as the initial value.  If no default value is defined in PCM and a defaultValue is specified in CML, the configurator uses the value defined in CML as the initial value of the variable.  See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| domainComputation | true, false | domainComputation is a CML annotation that specifies how the domain of a model element is determined, either by using a fixed domain or by computing the domain dynamically during configuration.  If domainComputation is not explicitly specified, the engine sets it implicitly as false for the variable. If the domainComputation is specified as true, the variable domain is dynamically determined based on the configuration and constraint logic. If the domainComputation is specified as false, the variable domain is fixed.  See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| nullAssignable | true, false | Sets an initial value for the calculated variable if the expression value can't be calculated. |
| Peelable | true, false | Indicates whether the constraint engine can override the variable’s value (whether set by default or user selection) to resolve a conflict (`true`) or not (`false`).  If set to `true`, the engine treats the value as a "soft selection." When a configuration conflict occurs, the engine attempts to "peel" (unbind) this variable and retry the solution. If a valid configuration is found, the engine automatically changes the value to satisfy constraints, rather than displaying an error message to the user. If not explicitly set, or set to false, the engine treats the value as a "hard selection." If the value causes a conflict with a constraint, the engine will not attempt to change it automatically. Instead, it will stop and display a conflict error message to the user, requiring manual intervention to resolve the issue. See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| productGroup | integer | Used to represent the group cardinality for relationships under a type, either for specified relationships, or for all relationships (using`\*`).  We recommend using `maxInstanceQty` and `minInstanceQty` type annotations instead of productGroup. See [Type Annotations](./cml_type_annotations.htm.md "You can annotate types to add information. Type annotations are metadata applied to a type declaration to provide instructions to the constraint engine regarding how instances of that type should be handled, instantiated, or used in the configuration structure."). |
| relatedAttributes | string value | relatedAttributesannotation is required to reset the domain to the original domain for domain computation.  If relatedAttributes annotation is not specified, the engine updates the variable domain according to domainComputation and constraint logic. If the relatedAttributes annotation is specified with one or multiple values (separated by comma), the variable domain is reset to the original domain.  See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| sequence | integer | Indicates the sequence in which variables are configured.  If a sequence value is not explicitly defined, the configurator implicitly determines the order based on the variable declaration order in the CML model.  If a sequence value is explicitly defined, the configurator uses the sequence number to control the order in which variables are configured. Variables with lower sequence values are assigned first. See examples [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| setDefault | true, false | Sets the variable status to default. |
| source | string value | Data source defined in the model. |
| sourceAttribute | Variable name in string | Sets the domain of the current variable to be the domain of the source variable. |
| strategy | descending, ascending, string | Defines the strategy to configure the variable.   - If the strategy is ascending, the engine tries values from low to high. - If the strategy is descending, the engine tries values from high to low.  See example [here](./cml_annotation_examples.htm.md "Constraint Modeling Language (CML) annotations are labels that you add to parts of a model, such as types, variables, relationships, and constraints. Annotations control how these elements are shown and how they behave in the configurator. Annotations help fine-tune the configurator and the constraint engine without changing the actual structure of the model."). |
| tagName | string value | To create an external variable linked to a Sales Transaction header, use the tagName annotation with the contextPath annotation to reference context tags on SalesTransactionItem within a type. See contextPath in [External Variable Annotations](./cml_external_variables.htm.md "External variables are global Constraint Modeling Language (CML) variables defined within a virtual CML type."). |
