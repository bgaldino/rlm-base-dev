---
page_id: cml-constraints
title: Constraints
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-constraints.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-core-concepts
legacy_page_id: cml_constraints.htm
fetched_at: 2026-11-25
---

# Constraints

Constraints enforce rules and conditions on types, variables, and relationships. Use constraints to define logical restrictions and ensure consistency within the model.

Every variable in a configuration carries a `cfgStatus` value that records how its current value was set. The constraint engine uses `cfgStatus` to decide whether it can change a variable’s value while solving. A variable’s `cfgStatus` is one of these values.

- `User` A user manually set the value during configuration. The constraint engine treats this value as fixed.

- `Default` A `setDefault` or `preference` rule set the value. The constraint engine can override this value while solving.

- `Engine` The constraint engine set the value to satisfy a constraint.

Constraints skip any variable whose `cfgStatus` is `User`. As a result, a constraint that would otherwise change the variable has no effect on a user-set value. To enforce a value regardless of user input, make sure no user-set value conflicts with the constraint.

**Note:**

In some conditions, the constraint engine can override a value set by a user. If this happens, contact Salesforce Customer Support.

For more information about the supported constraints, see:

- [Logical Constraints](./cml-logical-constraints.md)

- [Table Constraints](./cml-table-constraints.md)

- [Using Proxy Variables with Constraints on Types and Relationships](./cml-using-proxy-variables-constraints.md)

- [Group Type](./cml-group-type.md)

- [Message Rule](./cml-message-rule.md)

- [Preference Rule](./cml-preference-rule.md)

- [Require Rule](./cml-require-rule.md)

- [Require Rule vs Constraint](./cml-require-rule-vs-constraint.md)

- [SetDefault Rule](./cml-setdefault-rule.md)

- [Exclude Rule](./cml-exclude-rule.md)

- [Action Rule](./cml-action-rule.md)

- [Hide/Disable Rule](./cml-hide-disable-rule.md)

- [Recommendation Rule](./cml-recommendation-rule.md)

- [Set Product Selling Model in a Constraint](./cml-set-product-selling-model-constraint.md)

## Supported Logic Operators

These logic operators are supported in CML.

## Arithmetic Operators

- Multiplication (*)

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

Here are the details of `abort`, a constraint annotation.

| Annotation | Possible Values | Description |
| --- | --- | --- |
| abort | true, false | Specifies that, if this constraint fails, abort search and return `false` for configuration. |

- 

**[Logical Constraints](./cml-logical-constraints.md)**

A logical constraint defines a statement that must hold true logically. The constraint can be any logical expression by using a logical operator.

- 

**[Table Constraints](./cml-table-constraints.md)**

The table constraint in Constraint Modeling Language (CML) is used to define a set of valid combinations of values for two or more attributes. These combinations are specified in rows within the constraint definition.

- 

**[Proxy Variables with Constraints on Types and Relationships](./cml-using-proxy-variables-constraints.md)**

Use proxy variables to reference the variables of related types, including parent, root, and sibling types.

- 

**[Message Rule](./cml-message-rule.md)**

The message rule displays a message to users based on specified conditions.

- 

**[Preference Rule](./cml-preference-rule.md)**

The preference rule encourages the constraint solver to satisfy the condition, but doesn’t enforce it if the condition can’t be met.

- 

**[Require Rule](./cml-require-rule.md)**

The require rule requires certain components to be included in a relationship when specified conditions are met.

- 

**[Require Rule vs Constraint](./cml-require-rule-vs-constraint.md)**

In Constraint Modeling Language (CML), constraint() and require() can both enforce behavior, but they operate differently: constraint focuses on logical consistency, require focuses on physical presence of products.

- 

**[Setdefault Rule](./cml-setdefault-rule.md)**

The setdefault rule allows component selection with attribute values and quantity, similar to the require rule.

- 

**[Exclude Rule](./cml-exclude-rule.md)**

The exclude rule automatically removes a specific type in a relationship if a certain condition is true.

- 

**[Action Rule](./cml-action-rule.md)**

The CML Action Rule is defined using the rule() keyword. Its primary purpose is to execute a designated action, specified as a string literal, when a condition is met.

- 

**[Hide or Disable Rule](./cml-hide-disable-rule.md)**

The Hide or Disable Rule uses the rule() keyword to conditionally remove an element from the selection menu (hide) or preserve it in the menu while preventing user selection (disable).

- 

**[Recommendation Rule](./cml-recommendation-rule.md)**

The recommend keyword is used within a Constraint Modeling Language (CML) rule to display suggestions for related products in the Product Configurator. The rule defines the condition under which a specific product type or relation should be suggested to the user.

- 

**[Set Product Selling Model in a Constraint](./cml-set-product-selling-model-constraint.md)**

Use the productSellingModel tagname to write a constraint that sets the Product Selling Model (PSM) for a type. You can define a PSM as one time, time-deferred (subscription with end date), or evergreen (recurring subscription with no preset end date). The PSM is updated for new line items at runtime, based on the constraint.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-constraints.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
