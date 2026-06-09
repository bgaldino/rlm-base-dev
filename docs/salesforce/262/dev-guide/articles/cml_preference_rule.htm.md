---
page_id: cml_preference_rule.htm
title: Preference Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_preference_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Preference Rule

The preference rule encourages the constraint solver to satisfy the condition, but
doesn't enforce it if the condition can't be met.

The system tries to satisfy the condition in a preference rule, but if for some
reason it can't, the system delivers a failure message to the user with `Info` severity.

The preference rule has this
syntax.

```
preference(logic expression, string literal | string variable, argument, .., argument);
preference(logic expression, string literal | string variable);
preference(logic expression);
```

A preference rule can include an optional explanation message for failure. The message is of
`Info` severity, meaning it does not block the user
from continuing with the action.

In this example, the preference rule encourages the user
to mention the `dBMax` value as `90` and the `requiredKW`
value as `500`.

```
type GeneratorSet {
   int requiredKW = [101..10000];
   int dBMax = [0..140];
   preference(dBMax == 90, "90 preferred for dbMax");
   preference(requiredKW == 500,"50 preferred for requiredKW");
}
```
