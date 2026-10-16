---
page_id: cml_setdefault_rule.htm
title: Setdefault Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_setdefault_rule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Setdefault Rule

The setdefault rule allows component selection with attribute values and quantity,
    similar to the require rule.

    
      

Unlike the require rule, the setdefault rule applies a default configuration status and
        uses a triggering mechanism to control when the solver attempts to satisfy the rule. The
        setdefault rule can include an optional explanation message.

      

The setdefault has this syntax, similar to the require rule.

      

```
setdefault(condition, expression, message);
```

      

The setdefault rule evaluates the condition. If the condition is false, the solver ignores
        the expression and doesn't display a message, regardless of whether any part of the
        condition is changed. If the condition is true, the solver performs one of these
        actions.

      
        
- If any part of the condition is changed or the parent component is new, the solver
          attempts to satisfy the expression. If the solver can't satisfy the expression, an
          explanation message is displayed (if included).

        
- If no part of the condition is changed, the solver evaluates the expression without
          attempting to satisfy it. If the expression evaluates to false, an explanation message is
          displayed (if included).

      

      

The key difference between the setdefault rule and the require rule is that the setdefault
        rule attempts to satisfy the expression only when a condition is changed. If no condition is
        changed, the setdefault rule performs a passive evaluation. The require rule always attempts
        to satisfy the expression when the condition is true.

      

In this scenario, we use the requiredKW attribute (the user's power requirement) as
        the condition and the Accessories relation as the target for the recommended
        cardinality.

      

```
type Accessory;
type GeneratorSet  {
int requiredKW = [101..10000];
relation Accessories : Accessory[1..99];
/**
* @Title High Power Accessory Recommendation
* The setdefault constraint specifies that 2 accessory units are
* recommended when the required power capacity is greater than 2000 kW.
*/
setdefault(
requiredKW > 2000,
Accessories[Accessory] == 2,
"2 specialized accessory kits are recommended for power levels above 2000 kW"
);
}
```
