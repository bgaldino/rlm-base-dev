---
page_id: cml_action_rule.htm
title: Action Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_action_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Action Rule

The CML Action Rule is defined using the rule() keyword. Its primary purpose is to
execute a designated action, specified as a string literal, when a condition is met.

This action is typically handled by external systems, such as the Product Configurator API
or custom code, to manage business processes, workflows, or complex constraints that fall
outside the constraint engine's primary scope.

Action rules have this syntax.

```
rule(condition, action, arg, ..., arg)
rule(<condition>, <action>, "attribute", <attribute>);
rule(<condition>, <action>, "attribute", <attribute>, "value", [<attribute values>]);
rule(<condition>, <action>, "relation", <relation>, "type", <type>);
```

`condition` is any logic expression such as a constraint
in CML.

`action` is a string literal that specifies an action
that can be interpreted by the Product Configurator API. The Product Configurator API
supports these actions.

- Hide: hide attribute, attribute value, product option
- Disable: disable attribute, attribute value, product option
- args are a list of arguments needed to execute the action. An argument is a pair
  including a string literal and an identifier, a literal, or a domain, enclosed in brackets
  [ ] to specify multiple values. The string literal specifies what kind of argument
  follows. The identifier attribute can be defined in the type. The engine retrieves the
  argument value and passes it to the caller to execute the action.
