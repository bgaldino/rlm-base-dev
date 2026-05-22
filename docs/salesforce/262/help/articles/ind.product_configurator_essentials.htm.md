---
article_id: ind.product_configurator_essentials.htm
title: Product Configurator Essentials
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_essentials.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Product Configurator Essentials

Browse through this collection of terms, key objects, and key concepts. This collection is designed to give Salesforce admins, sales reps, and developers a clear and consistent understanding of product configurator concepts and helps them navigate the Product Configuration landscape.

Action Rule
Use the rule to define simple conditions and action rules. When the conditions are met, the constraint solver engine raises the action with parameters, and the caller executes the action with those parameters. The action can be anything that the caller defines.
Actionable Rules
Rule outcomes that take programmatic action at the time of execution, such as auto-add and auto-remove.
Configuration Rule
A rule that includes a condition and an action block, where conditions are based on a product or a product class, and various actions are taken on one or more products and their attributes.
Configuration Logs
Diagnostic records that capture configuration behavior. Review these logs to validate CML code, analyze configuration clarity and accuracy, and troubleshoot constraints to make sure your constraint models perform as expected. The Product Configuration Constraints Designer permission set is required to enable configuration logs.
Constraint Engine
The engine that compiles Constraint Model Language (CML) code into a constraint model and uses the model to construct a product configuration that complies with the specified constraints.
Constraint Model
For product configuration, constraint models describe real-world entities and their relationships to each other. They enforce business logic without needing extensive coding, by using a special language designed for this purpose, Constraint Modeling Language.
Constraint Model Language (CML)
A domain-specific language that defines models for complex systems.
Constraint Type
In CML, you define types to represent the entities or objects in the model. Types are the foundational building blocks of CML. It consists of the property, relationships, constraints and rules for the entities. They’re similar to the classes in object-oriented programming.
Conditional Operator
Specifies the conditions that determine a result.
Constraint Relationship
Defines how different types are associated with one another.
Constraint Variable
Variables are the properties or characteristics defined within a type. Variables can hold different kinds of data, such as strings, numbers, and lists, and can be calculated from other values.
Default Product Configurator Flow
A predefined flow that's used as a template to create a customized product configuration flow based on business requirements.
Distinct Constraint
The constraint enforces unique values for a set of variables.
Equal Constraint
The constraint enforces equal values for all variables referred inside the constraint.
Error Component
The component serves as a central location for all errors, warnings, and informational messages related to the product that you’re configuring.
Exclude Rule
The rule is used to automatically remove a specific type in a relationship if a certain condition is met.
Exclusion Constraint
The constraint excludes certain values from a relationship variable. A relationship variable is a set of variables that define how different types, such as products and attributes, are connected or interact with each other within a relationship.
Flow Components
The predefined Configuration Flow Template is a collection of composable components, such as options, prices, quantities, and summaries. These components are extensible.
Flow Template Association
Associating the flow template to products or product classes for rendering during run time.
Implication Operator (→)
Enforces that if a precondition is true, the postcondition must also be true. If the precondition is false, the postcondition isn’t required.
In Set Operator
The operator enforces a constraint in which a variable value must be one of the defined values in the given domain.
Inclusion Constraint
The constraint enforces a relationship variable to include certain values. A relationship variable is a set of variables that define how different types (such as products and attributes) are connected or interact with each other within a relationship.
Indistinct Constraint
The constraint enforces non-uniqueness for variable values.
Instant Pricing
Toggle in the run-time sales rep experience to control the pricing calls made for each configuration change. Turning on Instant Pricing results in an instant change of prices shown in the summary component when any changes are made to product selections.
Logical Constraint
Defines a statement that must hold true logically. The constraint can be any logical expression that uses one of these logical operators: AND (&&), Conditional (?), Implication (→), Logical equivalent (<->), OR (||), XOR (^).
Logical Equivalence Operator (↔)
The conditional operator that specifies that two statements are logically equivalent, that is, they have the same truth value under all possible conditions. This operator is equivalent to the statement. If one statement is true, then the other must be true, and vice versa.
Message Component
The UI component that shows messages for warnings and errors that occur during configuration. The messages convey information, an error, an alert, or a warning.
Message Rule
The rule shows messages to users based on specified conditions.
Named Constraint
You can name a constraint, similar to naming a variable, and reference it later in the model.
Null Constraint
The constraint determines whether a variable is bound to a value (true) or not (false). The configurable annotation for the variable must be set to false, or the engine assigns a value to the variable, and the null constraint is false.
Option Cards
Individual product details are presented to the sales rep as part of a card that you can further expand for focused product configuration in the Configurator.
Option Group
A collection of products and components that are logically grouped together.
Preference Rule
The rule encourages the constraint solver to satisfy the condition, but doesn’t enforce it if the condition can’t be met.
Product Validation
Toggle in the runtime sales rep experience to validate that the current product configuration is accurate. Turning on Product Validation triggers qualification, Product Catalog Management validation, and configuration rules. Validating the configuration against product definitions and rule governance on-demand, rather than automatically with every selection, optimizes performance and enables users to resolve errors before saving.
Regular Expression Constraint
Use the constraint to determine if a string matches a regular expression.
Relationships
Create relationships to define how different types are connected to each other. For example, a relationship can specify a range for a type (in a constraint model for a house design, use a relationship to specify that the house must have between one and five rooms) or cardinality (the house must have exactly one bathroom) or order (the first room in the house design must be a living room, followed by one or more bedrooms). Relationships can have default quantities and variables.
Require Rule
The rule requires certain components in a relationship when specified conditions are met. Required components can have attributes and quantity specified. The Require rule can include an optional explanation message for failure explanation.
Rule Scope
The radius within which the rule condition is applied can be a product, bundle, or transaction.
Rule Sequence
A numerical sequence of rules that determines how they're executed at run time, also known as rule rank or rule priority.
Selected or Unselected Constraint
Use the constraint to determine if given values are selected or unselected for multiple selection variables.
Sequential Rule
This rule increments a relationship variable by an integer value, X, which is another variable of the same type. It's like a simplified loop. Use it to solve slotting issues, which involve arranging components efficiently in server setups.
Summary Component
The UI component that provides a comprehensive, real-time summary of the configured product bundle, reflecting updates instantly as selections are made. Sales reps get a focused view of the overall bundle structure, where selections are categorized by product to illustrate the hierarchy clearly. Beyond attributes, the component also shows a detailed pricing breakdown, including quantities and a full price waterfall for the specific configuration.
Table Constraint
 The constraints enforce value combinations for variables. The table constraint defines valid combinations of values, specified in rows.
Unequal Constraint
The constraint enforces unequal values for the given variables.
Untable Constraint
 The constraints enforce value combinations for variables. The untable constraint is the negation of the table constraint. It specifies that the variable values from different rows aren't valid in combination with each other.
Variables
The properties or characteristics that you define within a type. Variables can hold different kinds of data, such as strings, numbers, and lists.
Visibility Rules
Rule outcomes make visual updates to the configured product, for example, hide, disable, or exclude.
