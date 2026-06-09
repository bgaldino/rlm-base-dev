---
page_id: cml_constraints.htm
title: Constraints
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_constraints.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_cml_core_concepts.htm
fetched_at: 2026-06-09
---

# Constraints

Constraints enforce rules and conditions on types, variables, and relationships. Use
constraints to define logical restrictions and ensure consistency within the
model.

For more information about the supported constraints, see:

- [Logical
  Constraints](./cml_logical_constraints.htm.md "A logical constraint defines a statement that must hold true logically. The constraint can be any logical expression by using a logical operator.")
- [Table
  Constraints](./cml_table_constraints.htm.md "The table constraint in Constraint Modeling Language (CML) is used to define a set of valid combinations of values for two or more attributes. These combinations are specified in rows within the constraint definition.")
- [Using Proxy Variables with Constraints on Types and Relationships](./cml_using_proxy_variables_constraints.htm.md "Use proxy variables to reference the variables of related types, including parent, root, and sibling types.")
- [Group Type](./cml_group_type.htm.md "In Constraint Modeling Language (CML), a Group Type is used to logically containerize related components within a bundle configuration, primarily when product component groups are imported from Product Catalog Management (PCM).")
- [Message Rule](./cml_message_rule.htm.md "The message rule displays a message to users based on specified conditions.")
- [Preference Rule](./cml_preference_rule.htm.md "The preference rule encourages the constraint solver to satisfy the condition, but doesn't enforce it if the condition can't be met.")
- [Require Rule](./cml_require_rule.htm.md "The require rule requires certain components to be included in a relationship when specified conditions are met.")
- [Require Rule vs Constraint](./cml_require_rule_vs_constraint.htm.md "In Constraint Modeling Language (CML), constraint() and require() can both enforce behavior, but they operate differently: constraint focuses on logical consistency, require focuses on physical presence of products.")
- [SetDefault Rule](./cml_setdefault_rule.htm.md "The setdefault rule allows component selection with attribute values and quantity, similar to the require rule.")
- [Exclude Rule](./cml_exclude_rule.htm.md "The exclude rule is used to automatically remove a specific type in a relationship if a certain condition is met.")
- [Action Rule](./cml_action_rule.htm.md "The CML Action Rule is defined using the rule() keyword. Its primary purpose is to execute a designated action, specified as a string literal, when a condition is met.")
- [Hide/Disable Rule](./cml_hide_disable_rule.htm.md "The Hide or Disable Rule uses the rule() keyword to conditionally remove an element from the selection menu (hide) or preserve it in the menu while preventing user selection (disable).")
- [Recommendation Rule](./cml_recommendation_rule.htm.md "The recommend keyword is used within a Constraint Modeling Language (CML) rule to display suggestions for related products in the Product Configurator. The rule defines the condition under which a specific product type or relation should be suggested to the user.")
- [Set Product Selling Model in a Constraint](./cml_set_product_selling_model_constraint.htm.md "Use the productSellingModel tagname to write a constraint that sets the Product Selling Model (PSM) for a type. You can define a PSM as one time, time-deferred (subscription with end date), or evergreen (recurring subscription with no preset end date). The PSM is updated for new line items at runtime, based on the constraint.")

## Supported Logic Operators

These logic operators are supported in CML.

## Arithmetic Operators

- Multiplication (\*)
- Division (/)
- Remainder (%)
- Addition (+)
- Subtraction (-)

## Relational Operators

- Greater than (>)
- Greater than or equal to (>=)
- Less than (<)
- Less than or equal to (<=)

## Equality Operators

- Equal (==)
- Not equal (!=)

## Logic Operators

- Not (!)
- And (&&)
- XOR/Exclusive or (^)
- Or (||)
- Bi-conditional (<->)
- Conditional (?:)
- Implication (->)

## Operator Precedence

In resolving equations, operator precedence determines the order in which operations are performed. Operators in CML have precedence in this order:

- Arithmetic operators have the first precedence.
- Relational operators have the second precedence.
- Equality operators have the third precedence.
- Logic operators have a lower precedence than equality operators, in decreasing order as listed, with Implication having the lowest precedence.

## Constraint Annotation

Here are the details of `abort`, a constraint
annotation.

| Annotation | Possible Values | Description |
| --- | --- | --- |
| abort | true, false | Specifies that, if this constraint fails, abort search and return `false` for configuration. |

- **[Logical Constraints](./cml_logical_constraints.htm.md)**  
  A logical constraint defines a statement that must hold true logically. The constraint can be any logical expression by using a logical operator.
- **[Table Constraints](./cml_table_constraints.htm.md)**  
  The table constraint in Constraint Modeling Language (CML) is used to define a set of valid combinations of values for two or more attributes. These combinations are specified in rows within the constraint definition.
- **[Proxy Variables with Constraints on Types and Relationships](./cml_using_proxy_variables_constraints.htm.md)**  
  Use proxy variables to reference the variables of related types, including parent, root, and sibling types.
- **[Message Rule](./cml_message_rule.htm.md)**  
  The message rule displays a message to users based on specified conditions.
- **[Preference Rule](./cml_preference_rule.htm.md)**  
  The preference rule encourages the constraint solver to satisfy the condition, but doesn't enforce it if the condition can't be met.
- **[Require Rule](./cml_require_rule.htm.md)**  
  The require rule requires certain components to be included in a relationship when specified conditions are met.
- **[Require Rule vs Constraint](./cml_require_rule_vs_constraint.htm.md)**  
  In Constraint Modeling Language (CML), constraint() and require() can both enforce behavior, but they operate differently: constraint focuses on logical consistency, require focuses on physical presence of products.
- **[Setdefault Rule](./cml_setdefault_rule.htm.md)**  
  The setdefault rule allows component selection with attribute values and quantity, similar to the require rule.
- **[Exclude Rule](./cml_exclude_rule.htm.md)**  
  The exclude rule is used to automatically remove a specific type in a relationship if a certain condition is met.
- **[Action Rule](./cml_action_rule.htm.md)**  
  The CML Action Rule is defined using the rule() keyword. Its primary purpose is to execute a designated action, specified as a string literal, when a condition is met.
- **[Hide or Disable Rule](./cml_hide_disable_rule.htm.md)**  
  The Hide or Disable Rule uses the rule() keyword to conditionally remove an element from the selection menu (hide) or preserve it in the menu while preventing user selection (disable).
- **[Recommendation Rule](./cml_recommendation_rule.htm.md)**  
  The recommend keyword is used within a Constraint Modeling Language (CML) rule to display suggestions for related products in the Product Configurator. The rule defines the condition under which a specific product type or relation should be suggested to the user.
- **[Set Product Selling Model in a Constraint](./cml_set_product_selling_model_constraint.htm.md)**  
  Use the productSellingModel tagname to write a constraint that sets the Product Selling Model (PSM) for a type. You can define a PSM as one time, time-deferred (subscription with end date), or evergreen (recurring subscription with no preset end date). The PSM is updated for new line items at runtime, based on the constraint.
